def generate_prompt(user_input, context=None):
    prompt_template = "User: {}\nAI: "
    if context:
        prompt_template = "Context: {}\n" + prompt_template
        return prompt_template.format(context, user_input)
    return prompt_template.format(user_input)

def format_response(response):
    return response.strip() if response else "No response generated."