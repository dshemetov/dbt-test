-- macros/has_aws_credentials.sql
{% macro has_aws_credentials() %}
  {% if env_var('AWS_ACCESS_KEY_ID', '') != '' and env_var('AWS_SECRET_ACCESS_KEY', '') != '' %}
    {{ return(true) }}
  {% else %}
    {{ return(false) }}
  {% endif %}
{% endmacro %}