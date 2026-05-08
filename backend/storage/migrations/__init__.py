"""Versioned storage migrations.

Migration filenames use a zero-padded numeric prefix. The runner imports them
in lexical order and calls each module's ``apply(conn)`` function once.
"""
