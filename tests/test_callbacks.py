import unittest
from types import SimpleNamespace

from ai_news_podcast import callbacks, config


class Tool:
    def __init__(self, name):
        self.name = name


def ctx():
    return SimpleNamespace(state={})


class TestBlocklist(unittest.TestCase):
    def test_blocks_site_operator(self):
        out = callbacks.block_unwanted_domains_callback(
            Tool("google_search"), {"query": "nvidia news site:reddit.com"}, ctx())
        self.assertEqual(out["error"], "blocked_source")

    def test_blocks_plain_domain(self):
        out = callbacks.block_unwanted_domains_callback(
            Tool("google_search"), {"query": "ai news from wikipedia.org"}, ctx())
        self.assertEqual(out["error"], "blocked_source")

    def test_allows_normal_query(self):
        out = callbacks.block_unwanted_domains_callback(
            Tool("google_search"), {"query": "latest AI news NASDAQ"}, ctx())
        self.assertIsNone(out)

    def test_no_false_positive_on_common_word(self):
        out = callbacks.block_unwanted_domains_callback(
            Tool("google_search"), {"query": "medium-sized AI startups raising funds"}, ctx())
        self.assertIsNone(out)

    def test_ignores_other_tools(self):
        out = callbacks.block_unwanted_domains_callback(
            Tool("get_financial_context"), {"query": "site:reddit.com"}, ctx())
        self.assertIsNone(out)


class TestWhitelistAndFreshness(unittest.TestCase):
    def test_whitelist_appended(self):
        args = {"query": "AI news"}
        callbacks.filter_news_sources_callback(Tool("google_search"), args, ctx())
        for d in config.WHITELIST_DOMAINS:
            self.assertIn(f"site:{d}", args["query"])

    def test_whitelist_not_duplicated(self):
        args = {"query": "AI news site:techcrunch.com"}
        callbacks.filter_news_sources_callback(Tool("google_search"), args, ctx())
        self.assertEqual(args["query"], "AI news site:techcrunch.com")

    def test_freshness_added_once(self):
        args = {"query": "AI news"}
        callbacks.enforce_data_freshness_callback(Tool("google_search"), args, ctx())
        callbacks.enforce_data_freshness_callback(Tool("google_search"), args, ctx())
        self.assertEqual(args["query"].count("tbs=qdr:w"), 1)


class TestProcessLog(unittest.TestCase):
    def test_injects_domains(self):
        c = ctx()
        resp = "see https://techcrunch.com/a and https://theverge.com/b"
        out = callbacks.inject_process_log_after_search(Tool("google_search"), {}, c, resp)
        self.assertEqual(out["search_results"], resp)
        self.assertIn("techcrunch.com", out["process_log"][0])
        self.assertIn("theverge.com", out["process_log"][0])

    def test_non_search_tool_unchanged(self):
        out = callbacks.inject_process_log_after_search(Tool("save_news_to_markdown"), {}, ctx(), "x")
        self.assertEqual(out, "x")

    def test_non_string_response_unchanged(self):
        resp = {"a": 1}
        out = callbacks.inject_process_log_after_search(Tool("google_search"), {}, ctx(), resp)
        self.assertIs(out, resp)


if __name__ == "__main__":
    unittest.main()
