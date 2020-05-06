""" Content init module
"""
try:
    from Products.Archetypes import atapi
    archetypes_installed = True
except ImportError:
    archetypes_installed = False

if archetypes_installed:
    from Products.validation.config import validation
    from eea.sparql.content.validators import SparqlQueryValidator
    validation.register(SparqlQueryValidator('isSparqlOverLimit'))