import os
import re

def escape_js_string(text):
    """
    Escape a string for embedding in JavaScript
    """
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def render_template(template_path, context=None):
    """
    Simple template renderer that replaces {{key}} placeholders with values from context.
    
    Args:
        template_path (str): Path to the template file
        context (dict): Dictionary containing values to replace in the template
    
    Returns:
        str: Rendered template as a string
    """
    if context is None:
        context = {}
        
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Perform special handling for ansi_art to escape for JavaScript
    if 'ansi_art' in context:
        context['ansi_art'] = escape_js_string(context['ansi_art'])
    
    # Replace {{key}} placeholders
    for key, value in context.items():
        placeholder = '{{' + key + '}}'
        template_content = template_content.replace(placeholder, str(value))
    
    return template_content
