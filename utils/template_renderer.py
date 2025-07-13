"""
Template rendering utilities for PixelPipe.

This module provides simple template rendering functionality
for generating HTML files with dynamic content.
"""

import os
import re

def escape_js_string(text):
    """
    Escape a string for embedding in JavaScript
    """
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def _simple_template_engine(template_content, context):
    """
    Simple template engine for variable substitution.
    
    Replaces {{variable}} placeholders with values from context dictionary.
    
    Args:
        template_content (str): Template string with {{variable}} placeholders
        context (dict): Dictionary of variable names and values
        
    Returns:
        str: Template with variables substituted
    """
    result = template_content
    for key, value in context.items():
        placeholder = f'{{{{{key}}}}}'
        result = result.replace(placeholder, str(value))
    return result

def render_template(template_path, context=None):
    """
    Render a template file with the given context.
    
    Args:
        template_path (str): Path to the template file
        context (dict): Dictionary of variables to substitute
        
    Returns:
        str: Rendered template content
        
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if context is None:
        context = {}
        
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Perform special handling for ansi_art to escape for JavaScript
    if 'ansi_art' in context:
        context['ansi_art'] = escape_js_string(context['ansi_art'])
    
    return _simple_template_engine(template_content, context)
