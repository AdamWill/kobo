#!/usr/bin/python
# -*- coding: utf-8 -*-


import unittest
import run_tests # set sys.path

import os
import shutil
import tempfile

from kobo.shortcuts import *


class TestEnum(unittest.TestCase):
    def test_force_list(self):
        self.assertEqual(force_list("a"), ["a"])
        self.assertEqual(force_list(["a"]), ["a"])
        self.assertEqual(force_list(["a", "b"]), ["a", "b"])
        
    def test_force_tuple(self):
        self.assertEqual(force_tuple("a"), ("a",))
        self.assertEqual(force_tuple(("a",)), ("a",))
        self.assertEqual(force_tuple(("a", "b")), ("a", "b"))

    def test_allof(self):
        self.assertEqual(allof(), True)
        self.assertEqual(allof(1), True)
        self.assertEqual(allof(True), True)
        self.assertEqual(allof(True, 1, "a"), True)
        self.assertEqual(allof(0), False)
        self.assertEqual(allof(""), False)
        self.assertEqual(allof(None), False)

    def test_anyof(self):
        self.assertEqual(anyof(), False)
        self.assertEqual(anyof(1), True)
        self.assertEqual(anyof(True), True)
        self.assertEqual(anyof(True, 0, "a"), True)
        self.assertEqual(anyof(0), False)
        self.assertEqual(anyof(""), False)
        self.assertEqual(anyof(None), False)

    def test_noneof(self):
        self.assertEqual(noneof(), True)
        self.assertEqual(noneof(False), True)
        self.assertEqual(noneof(True), False)
        self.assertEqual(noneof(False, "", 0), True)
        self.assertEqual(noneof(True, "a", 1), False)
        self.assertEqual(noneof(False, "a", 1), False)
        self.assertEqual(noneof(0, True, False, "a"), False)

    def test_oneof(self):
        self.assertEqual(oneof(), False)
        self.assertEqual(oneof(True), True)
        self.assertEqual(oneof(False), False)
        self.assertEqual(oneof(0, False, "a"), True)
        self.assertEqual(oneof(0, True, False, "a"), False)
        self.assertEqual(oneof(1, True, "a"), False)
        self.assertEqual(oneof(0, False, ""), False)

    def test_is_empty(self):
        self.assertEqual(is_empty(None), True)
        self.assertEqual(is_empty([]), True)
        self.assertEqual(is_empty([1]), False)
        self.assertEqual(is_empty(()), True)
        self.assertEqual(is_empty((1,)), False)
        self.assertEqual(is_empty({}), True)
        self.assertEqual(is_empty(1), False)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_file = os.path.join(self.tmp_dir, "tmp_file")
        save_to_file(self.tmp_file, "test")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_save_to_file(self):
        save_to_file(self.tmp_file, "foo")
        self.assertEqual("\n".join(read_from_file(self.tmp_file)), "foo")

        save_to_file(self.tmp_file, "\nbar", append=True, mode=600)
        self.assertEqual("\n".join(read_from_file(self.tmp_file)), "foo\nbar")

        # append doesn't modify existing perms
        self.assertEqual(os.stat(self.tmp_file).st_mode & 0777, 0644)

        os.unlink(self.tmp_file)
        save_to_file(self.tmp_file, "foo", append=True, mode=0600)
        self.assertEqual(os.stat(self.tmp_file).st_mode & 0777, 0600)

    def test_run(self):
        ret, out = run("echo hello")
        self.assertEqual(ret, 0)
        self.assertEqual(out, "hello\n")

        ret, out = run("exit 1", can_fail=True)
        self.assertEqual(ret, 1)

        self.assertRaises(RuntimeError, run, "exit 1")

    def test_parse_checksum_line(self):
        line_text = "d4e64fc7f3c6849888bc456d77e511ca  shortcuts.py"
        checksum, path = parse_checksum_line(line_text)
        self.assertEqual(checksum, "d4e64fc7f3c6849888bc456d77e511ca")
        self.assertEqual(path, "shortcuts.py")

        line_binary = "d4e64fc7f3c6849888bc456d77e511ca *shortcuts.py"
        checksum, path = parse_checksum_line(line_binary)
        self.assertEqual(checksum, "d4e64fc7f3c6849888bc456d77e511ca")
        self.assertEqual(path, "shortcuts.py")

    def test_compute_file_checksums(self):
        self.assertEqual(compute_file_checksums(self.tmp_file, "md5"), dict(md5="098f6bcd4621d373cade4e832627b4f6"))
        self.assertEqual(compute_file_checksums(self.tmp_file, ["md5", "sha256"]), dict(md5="098f6bcd4621d373cade4e832627b4f6", sha256="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"))


class TestPaths(unittest.TestCase):
    def test_split_path(self):
        self.assertEqual(split_path(""), ["."])
        self.assertEqual(split_path("../"), [".."])
        self.assertEqual(split_path("/"), ["/"])
        self.assertEqual(split_path("//"), ["/"])
        self.assertEqual(split_path("///"), ["/"])
        self.assertEqual(split_path("/foo"), ["/", "foo"])
        self.assertEqual(split_path("/foo/"), ["/", "foo"])
        self.assertEqual(split_path("/foo//"), ["/", "foo"])
        self.assertEqual(split_path("/foo/bar"), ["/", "foo", "bar"])
        self.assertEqual(split_path("/foo//bar"), ["/", "foo", "bar"])

    def test_relative_path(self):
        self.assertEqual(relative_path("/foo", "/"), "foo")
        self.assertEqual(relative_path("/foo/", "/"), "foo/")
        self.assertEqual(relative_path("/foo", "/bar/"), "../foo")
        self.assertEqual(relative_path("/foo/", "/bar/"), "../foo/")
        self.assertEqual(relative_path("/var/www/template/index.html", "/var/www/html/index.html"), "../template/index.html")
        self.assertEqual(relative_path("/var/www/template/index.txt", "/var/www/html/index.html"), "../template/index.txt")
        self.assertEqual(relative_path("/var/www/template/index.txt", "/var/www/html/index.html"), "../template/index.txt")
        self.assertRaises(RuntimeError, relative_path, "/var/www/template/", "/var/www/html/index.html")


if __name__ == '__main__':
    unittest.main()
