def build_selectors_from_crawl(crawl_data: list) -> list:
    """
    Converts multi-page scraper output into a flat selector list.
    """

    selectors = []

    for page in crawl_data:

        url = page.get("url", "")

        # Buttons
        for btn in page.get("buttons", []):
            selectors.append({
                "type": "button",
                "selector": btn.get("selector", ""),
                "text": btn.get("text", ""),
                "page_url": url
            })

        # Inputs
        for inp in page.get("inputs", []):
            selectors.append({
                "type": "input",
                "selector": inp.get("selector", ""),
                "input_type": inp.get("type", "text"),
                "placeholder": inp.get("placeholder", ""),
                "page_url": url
            })

        # Links
        for link in page.get("links", []):
            selectors.append({
                "type": "link",
                "selector": link.get("selector", ""),
                "text": link.get("text", ""),
                "href": link.get("href", ""),
                "page_url": url
            })

    return selectors