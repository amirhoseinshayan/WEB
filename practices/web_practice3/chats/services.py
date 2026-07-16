def generate_mock_ai_response(conversation, user_message):
    """
    Generate a mock AI response for a conversation.

    This function does not call any real AI provider. It only simulates
    a response based on the selected AI model and optional assistant.
    """

    ai_model_name = conversation.ai_model.name
    provider = conversation.ai_model.provider

    assistant = conversation.assistant

    if assistant is not None:
        assistant_title = assistant.title
        assistant_hint = f" using assistant '{assistant_title}'"
    else:
        assistant_hint = ""

    user_content = user_message.content.strip()

    if len(user_content) > 120:
        user_content = f"{user_content[:117]}..."

    return (
        f"[Mock response from {provider} {ai_model_name}{assistant_hint}] "
        f"I received your message: \"{user_content}\". "
        f"This is a simulated AI response for the Web Practice 3 backend."
    )