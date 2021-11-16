import os
import tempfile
import unittest

from chainjacking import chainjacking


class TestChainJackingMethods(unittest.TestCase):

    def test_find_vulnerable_go_modules(self):
        go_modules = ['github.com/user-a/repo-a', 'github.com/user-b/repo-b']
        vulnerable_usernames = ['user-a']

        expected_result = ['github.com/user-a/repo-a']
        vulnerable_packages = chainjacking._filter_vulnerable_go_packages(go_modules, vulnerable_usernames)
        self.assertEqual(expected_result, list(vulnerable_packages))

    def test_normalize_go_module_path(self):
        expected = 'github.com/!a!sdas!dasd/si!x-cli@v0.0.7-alpha'
        path = 'github.com/ASdasDasd/siX-cli@v0.0.7-alpha'
        result = chainjacking._normalize_go_package_path(path)
        self.assertEqual(result, expected)

    def test_locate_go_module_dir_path(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            expected_go_mod_dir = os.path.join(temp_dir_path, 'github.com', 'user-a', 'noms@v0.0.0-20210406041509-33124142b7ea')
            os.makedirs(expected_go_mod_dir)

            module_url = 'github.com/user-a/noms'
            root_dir = temp_dir_path

            result = chainjacking._locate_go_package_dir_path(module_url, root_dir)
            self.assertEqual(expected_go_mod_dir, result)

    def test_parse_go_mod_graph_output(self):
        command_output = 'github.com/user-a/noms github.com/user-b/toml@v0.3.1\n\
        github.com/user-a/noms github.com/user-c/noms-gx@v0.0.0-20180714061401-d6cb97cb040b\n\
        github.com/user-a/noms github.com/user-d/kingpin@v2.2.6+incompatible\n'
        go_modules, github_usernames = chainjacking._parse_go_mod_graph_command_output(command_output)
        expected_go_modules, expected_github_usernames = [{'github.com/user-c/noms-gx@v0.0.0-20180714061401-d6cb97cb040b', 'github.com/user-d/kingpin@v2.2.6+incompatible', 'github.com/user-b/toml@v0.3.1'}, {'user-b', 'user-d', 'user-c'}]
        self.assertEqual(expected_go_modules, go_modules)
        self.assertEqual(expected_github_usernames, github_usernames)


if __name__ == '__main__':
    unittest.main()
