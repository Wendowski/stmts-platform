"""Deployment boundary tests: commands are stubbed, no network/server is contacted."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DeploymentTest(unittest.TestCase):
    def run_script(self, destination):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ('index.html', '.htaccess', 'deployment.json'):
                (base / name).write_text('fixture')
            bin_dir = base / 'bin'; bin_dir.mkdir()
            log = base / 'commands'
            for command in ('ssh', 'rsync'):
                executable = bin_dir / command
                executable.write_text('#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$COMMAND_LOG"\n')
                executable.chmod(0o700)
            env = dict(os.environ, PATH=str(bin_dir)+':'+os.environ['PATH'], COMMAND_LOG=str(log), DH_HOST='server.dreamhost.com', DH_USER='previewuser', DH_PATH=destination)
            result = subprocess.run(['bash', str(ROOT/'infra/dreamhost/deploy-preview.sh'), str(base)], env=env, capture_output=True)
            return result.returncode, log.read_text().splitlines() if log.exists() else []

    def test_index_then_revision_published_after_assets(self):
        code, commands = self.run_script('/home/previewuser/preview.example.com')
        self.assertEqual(code, 0)
        self.assertEqual(len(commands), 4)
        self.assertIn('StrictHostKeyChecking=yes', commands[0])
        self.assertIn('.stmts-preview-root', commands[0])
        self.assertIn('--exclude=index.html', commands[1])
        self.assertIn('index.html', commands[2])
        self.assertIn('deployment.json', commands[3])
        self.assertFalse(any('--delete' in command for command in commands))

    def test_unsafe_destinations_fail_before_ssh(self):
        for path in ('/', '/home/previewuser', '/home/other/site', '/home/previewuser/../site', '/home/previewuser/site;touch hacked'):
            code, commands = self.run_script(path)
            self.assertNotEqual(code, 0)
            self.assertEqual(commands, [])

if __name__ == '__main__':
    unittest.main()
