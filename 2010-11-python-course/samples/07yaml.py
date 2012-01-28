import sys
import yaml  # from http://pyyaml.org/

value = """
- name: John Smith
  age: 33
- name: Mary Smith
  age: 27
"""

print yaml.load(value)