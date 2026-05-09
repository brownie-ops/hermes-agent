def _agent(provider="custom", base_url="https://gua.guagua.uk/v1", api_mode="chat_completions"):
    from run_agent import AIAgent

    agent = AIAgent.__new__(AIAgent)
    agent.provider = provider
    agent.base_url = base_url
    agent.api_mode = api_mode
    agent.model = "test-model"
    agent.tools = []
    agent.max_tokens = 128
    agent.reasoning_config = None
    agent.request_overrides = {}
    agent.session_id = "test-session"
    agent.providers_allowed = []
    agent.providers_ignored = []
    agent.providers_order = []
    agent.provider_sort = None
    agent.provider_require_parameters = False
    agent.provider_data_collection = None
    agent._base_url_lower = base_url.lower()
    agent._base_url_hostname = ""
    agent._ollama_num_ctx = None
    agent._ephemeral_max_output_tokens = None
    agent._resolved_api_call_timeout = lambda: 30
    return agent


def _messages():
    return [
        {"role": "user", "content": "inspect something"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_probe",
                    "type": "function",
                    "function": {"name": "noop_probe", "arguments": "{}"},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_probe", "content": "{}"},
    ]


def test_jingua_chat_completion_empty_tool_call_content_is_null_in_api_copy_only():
    agent = _agent(provider="custom", base_url="https://gua.guagua.uk/v1")
    original = _messages()

    normalized = agent._normalize_empty_tool_call_content_for_api(original)

    assert normalized[1]["content"] is None
    assert original[1]["content"] == ""
    assert normalized[1] is not original[1]
    assert normalized[1]["tool_calls"] is not original[1]["tool_calls"]


def test_google_chat_completion_empty_tool_call_content_is_null_in_api_copy_only():
    agent = _agent(
        provider="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/chat/completions",
    )
    original = _messages()

    normalized = agent._normalize_empty_tool_call_content_for_api(original)

    assert normalized[1]["content"] is None
    assert original[1]["content"] == ""


def test_non_target_provider_preserves_empty_tool_call_content_and_object_identity():
    agent = _agent(provider="custom", base_url="https://example.invalid/v1")
    original = _messages()

    normalized = agent._normalize_empty_tool_call_content_for_api(original)

    assert normalized is original
    assert normalized[1]["content"] == ""


def test_non_empty_tool_call_content_is_not_modified_for_target_provider():
    agent = _agent(provider="custom", base_url="https://gua.guagua.uk/v1")
    original = _messages()
    original[1]["content"] = "Tool call requested."

    normalized = agent._normalize_empty_tool_call_content_for_api(original)

    assert normalized is original
    assert normalized[1]["content"] == "Tool call requested."


def test_native_modes_do_not_apply_chat_completion_compatibility_shim():
    agent = _agent(
        provider="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/chat/completions",
        api_mode="codex_responses",
    )
    original = _messages()

    normalized = agent._normalize_empty_tool_call_content_for_api(original)

    assert normalized is original
    assert normalized[1]["content"] == ""


def test_build_api_kwargs_sends_normalized_copy_to_chat_transport():
    agent = _agent(provider="custom", base_url="https://gua.guagua.uk/v1")
    original = _messages()

    class _Transport:
        def build_kwargs(self, **kwargs):
            return kwargs

    agent._get_transport = lambda: _Transport()

    api_kwargs = agent._build_api_kwargs(original)

    assert api_kwargs["messages"][1]["content"] is None
    assert original[1]["content"] == ""
