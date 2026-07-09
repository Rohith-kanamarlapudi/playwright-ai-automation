"""
Deterministic safety net for `expect_page()` misuse in LLM-generated
Playwright code.
 
The prompts already tell the model "Never use expect_page() unless a
popup is explicitly opened", and code_gen_agent has a heuristic check
for this — but both are just requests to the LLM / a string check that
is trivially defeated (e.g. the model's own idiomatic variable name
`popup_info` contains the substring "popup", which silently satisfies
a naive `"popup" not in code.lower()` check even when no real popup is
involved). A `with page.context.expect_page():` block that never
actually gets a "page" event will hang for the full default timeout
(30s) and fail the test.
 
This module removes that class of bug at the source: it parses the
generated code with `ast`, and for each test function, strips any
`expect_page()` with-block that isn't backed by real evidence in that
same function (an explicit target="_blank" click). Everything
downstream that depended on the removed popup variable (e.g.
`popup = popup_info.value`, `popup.wait_for_load_state()`) is removed
too, so the result always stays syntactically and referentially valid.
"""
 
import ast
 
 
def _calls_expect_page(item: ast.withitem) -> bool:
    call = item.context_expr
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr == "expect_page"
 
 
def _references_name(stmt: ast.AST, name: str) -> bool:
    return any(
        isinstance(n, ast.Name) and n.id == name for n in ast.walk(stmt)
    )
 
 
class _PopupSanitizer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        fn_source = ast.unparse(node)
        has_real_popup = (
            'target="_blank"' in fn_source or "target='_blank'" in fn_source
        )
        node.body = self._sanitize_block(node.body, has_real_popup)
        return node
 
    def _sanitize_block(self, body: list, has_real_popup: bool) -> list:
        new_body: list = []
        drop_names: set[str] = set()
 
        for stmt in body:
            # A later statement that references a name derived from a
            # popup block we already removed must go too. If it's an
            # assignment (e.g. `popup = popup_info.value`), cascade:
            # the name it defines is now undefined and must be dropped
            # for any statements after it as well.
            if drop_names and any(_references_name(stmt, n) for n in drop_names):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            drop_names.add(target.id)
                continue
 
            if (
                isinstance(stmt, ast.With)
                and len(stmt.items) == 1
                and _calls_expect_page(stmt.items[0])
            ):
                if has_real_popup:
                    new_body.append(stmt)
                    continue
 
                item = stmt.items[0]
                if isinstance(item.optional_vars, ast.Name):
                    drop_names.add(item.optional_vars.id)
 
                # Keep the with-block's own inner statements (e.g. the
                # page.click() that was inside it), just drop the
                # expect_page() wrapper around them.
                new_body.extend(self._sanitize_block(stmt.body, has_real_popup))
                continue
 
            new_body.append(stmt)
 
        return new_body if new_body else [ast.Pass()]
 
 
def sanitize_unjustified_popups(code: str) -> str:
    """
    Strip any expect_page() usage not backed by a real target="_blank"
    click in the same test function. Returns the code unmodified if it
    can't be parsed or doesn't mention expect_page() at all — the
    existing syntax check downstream still catches unparsable code.
    """
    if "expect_page(" not in code:
        return code
 
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
 
    tree = _PopupSanitizer().visit(tree)
    ast.fix_missing_locations(tree)
 
    try:
        return ast.unparse(tree)
    except Exception:
        return code