from hooks.pre_gen_project import setup
from hooks.post_gen_project import clean_up
import os
import sys


def test_virtualenv():
    setup()
    clean_up()

