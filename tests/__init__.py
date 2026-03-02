# Tests structure:
#
# Tests do not intend to test the argparse, just our behavior.
#
# In test_args, test_opts, test_flags runtime and typing are tested simultaneously.
# Typing tests rely on `typing.assert_type` to match the exact type and
# `fix.assert_compat` to ensure type is compatible with the stated one.
#
# `mypy` and `pyright` agree on a same assert_type. The `ty` is a rebel and do it own way.
# `assert_type` tests are suppressed for the `ty` (but `assert_compat` is still here)
#
