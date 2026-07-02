import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.books_page import BooksPage
from pages.admin_books_page import AdminBooksPage
from utils.screenshot_manager import screenshot_on_failure

@pytest.mark.login
class TestLogin:
    @screenshot_on_failure
    def test_login_page_loads(self, logged_out_page):
        login_page = LoginPage(logged_out_page)
        assert login_page.is_visible("login_username_input")
        assert login_page.is_visible("login_password_input")
        assert login_page.is_visible("login_submit_button")

    @screenshot_on_failure
    def test_login_valid_redirects_dashboard(self, authenticated_user_page):
        dashboard = DashboardPage(authenticated_user_page)
        assert dashboard.is_dashboard_visible()

    @screenshot_on_failure
    def test_login_invalid_shows_error(self, logged_out_page):
        login = LoginPage(logged_out_page)
        login.login("invalid_user", "wrong_password")
        error = login.get_error_message()
        assert "Invalid credentials" in error

@pytest.mark.books_user
class TestBooksUser:
    @screenshot_on_failure
    def test_search_existing_book(self, authenticated_user_page, test_data):
        books = BooksPage(authenticated_user_page)
        existing = test_data["books"]["existing_title"]
        books.search_book(existing)
        results = books.get_search_results()
        assert existing in results

    @screenshot_on_failure
    def test_search_non_existent_book(self, authenticated_user_page):
        books = BooksPage(authenticated_user_page)
        books.search_book("XYZ_NonExistent_999")
        message = books.get_no_results_message()
        assert "No results found" in message

    @screenshot_on_failure
    def test_search_empty_string(self, authenticated_user_page):
        books = BooksPage(authenticated_user_page)
        books.search_book("")
        hint = books.get_empty_search_hint()
        assert "Please enter a search term" in hint

    @screenshot_on_failure
    def test_borrow_available_book(self, authenticated_user_page, test_data):
        books = BooksPage(authenticated_user_page)
        book_title = test_data["books"]["available_title"]
        books.borrow_book(book_title)
        status = books.get_book_status(book_title)
        assert "Borrowed" in status

    @screenshot_on_failure
    def test_borrow_already_borrowed_book(self, authenticated_user_page, test_data):
        books = BooksPage(authenticated_user_page)
        book_title = test_data["books"]["already_borrowed_title"]
        books.borrow_book(book_title)
        error = books.get_borrow_error()
        assert "already borrowed" in error.lower()

    @screenshot_on_failure
    def test_borrow_non_existent_book(self, authenticated_user_page):
        books = BooksPage(authenticated_user_page)
        books.borrow_book("Non Existent Book")
        error = books.get_borrow_error()
        assert "not found" in error.lower()

    @screenshot_on_failure
    def test_return_borrowed_book(self, authenticated_user_page, test_data):
        books = BooksPage(authenticated_user_page)
        book_title = test_data["books"]["borrowed_title"]
        books.return_book(book_title)
        status = books.get_book_status(book_title)
        assert "Available" in status

    @screenshot_on_failure
    def test_return_already_returned_book(self, authenticated_user_page, test_data):
        books = BooksPage(authenticated_user_page)
        book_title = test_data["books"]["available_title"]
        books.return_book(book_title)
        error = books.get_return_error()
        assert "already returned" in error.lower()

    @screenshot_on_failure
    def test_return_non_existent_book(self, authenticated_user_page):
        books = BooksPage(authenticated_user_page)
        books.return_book("Non Existent Book")
        error = books.get_return_error()
        assert "not found" in error.lower()

@pytest.mark.admin
class TestAdminBooks:
    @screenshot_on_failure
    def test_add_book_valid(self, authenticated_admin_page, sample_book):
        admin = AdminBooksPage(authenticated_admin_page)
        admin.add_book(sample_book["title"], sample_book["author"], sample_book["isbn"])
        assert admin.is_book_in_list(sample_book["title"])

    @screenshot_on_failure
    def test_add_book_missing_fields(self, authenticated_admin_page):
        admin = AdminBooksPage(authenticated_admin_page)
        admin.add_book("", "", "")
        errors = admin.get_validation_errors()
        assert "Title is required" in errors

    @screenshot_on_failure
    def test_delete_book(self, authenticated_admin_page, test_data):
        admin = AdminBooksPage(authenticated_admin_page)
        book_title = test_data["books"]["existing_title"]
        admin.delete_book(book_title)
        assert not admin.is_book_in_list(book_title)

    @screenshot_on_failure
    def test_delete_non_existent_book(self, authenticated_admin_page):
        admin = AdminBooksPage(authenticated_admin_page)
        admin.delete_book("NonExist999")
        error = admin.get_delete_error()
        assert "not found" in error.lower()

    @screenshot_on_failure
    def test_update_book(self, authenticated_admin_page, test_data, sample_book):
        admin = AdminBooksPage(authenticated_admin_page)
        book_title = test_data["books"]["existing_title"]
        new_title = sample_book["title"]
        updated_details = {"title": new_title, "author": sample_book["author"]}
        admin.update_book(book_title, updated_details)
        assert admin.is_book_in_list(new_title)

    @screenshot_on_failure
    def test_update_book_invalid_data(self, authenticated_admin_page, test_data):
        admin = AdminBooksPage(authenticated_admin_page)
        book_title = test_data["books"]["existing_title"]
        invalid_details = {"title": "", "author": "   "}
        admin.update_book(book_title, invalid_details)
        errors = admin.get_validation_errors()
        assert "Title cannot be empty" in errors

@pytest.mark.access_control
class TestAccessControl:
    @screenshot_on_failure
    def test_non_admin_cannot_access_admin_pages(self, authenticated_user_page):
        user_page = authenticated_user_page
        user_page.goto("/admin/books")
        assert "Access Denied" in user_page.text_content("body")

@pytest.mark.ui
class TestUI:
    @screenshot_on_failure
    def test_mobile_viewport(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        login = LoginPage(page)
        login.navigate("/login")
        assert login.is_visible("login_submit_button")
        # Verify layout adapts – check elements are within viewport
        bounding = page.locator("#login-username").bounding_box()
        assert bounding is not None and bounding["x"] >= 0

    @screenshot_on_failure
    def test_keyboard_navigation(self, page):
        page.goto("/login")
        page.locator("#login-username").focus()
        page.keyboard.press("Tab")
        assert page.locator("#login-password").is_focused()
        page.keyboard.press("Tab")
        assert page.locator("button[type='submit']").is_focused()
        page.keyboard.press("Enter")
        # after login with invalid credentials to remain on page
        login = LoginPage(page)
        login.login("", "")
        error = login.get_error_message()
        assert len(error) > 0

    @screenshot_on_failure
    def test_headings_semantic_structure(self, page):
        page.goto("/login")
        headings = page.locator("h1, h2, h3, h4")
        count = headings.count()
        assert count >= 1
        for i in range(count):
            text = headings.nth(i).text_content().strip()
            assert len(text) > 0

@pytest.mark.error_handling
class TestErrorHandling:
    @screenshot_on_failure
    def test_network_timeout_message(self, page):
        # Simulate offline mode
        page.route("**/*", lambda route: route.abort("timedout"))
        login = LoginPage(page)
        login.navigate("/login")
        error_msg = page.locator(".network-error")
        assert error_msg.is_visible()
        assert "timeout" in error_msg.text_content().lower()