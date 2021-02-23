import os
import re
import typing
import sys
import yaml


class Konform(object):

    def __init__(self, root_dir: str = "."):
        """Create a new Konform runner on a specified root directory.

        Keyword arguments:
        root_dir -- the root directory (default '.')
        """
        
        self._problems: int = 0
        self._warnings: int = 0
        self._checks: int = 0
        self._root_dir: str = root_dir

    def run(self):
        """Runs Konform on the root directory it was initialized on.
        Prints the total number of problems and warnings.
        Exits with a different exit code based on whether
        there were problems (exit code 1), warnings (exit code 2)
        or none of both (exit code 0).
        """

        self._check_kustomize_tree(self._root_dir)

        print(f"problems detected: {self._problems}")
        print(f"warnings detected: {self._warnings}")

        if self._problems > 0:
            sys.exit(1)
        elif self._warnings > 0:
            sys.exit(2)
        else:
            sys.exit(0)

    def _report_problem(self, message: str):
        """Prints a problem report using a specified message.

        Keyword arguments:
        message -- the message that describes the problem
        """

        print(f"  \u274C {message}")
        self._problems += 1

    def _report_warning(self, message: str):
        """Prints a warning report using a specified message.

        Keyword arguments:
        message -- the message that describes the warning
        """

        print(f"  \u26A0 {message}")
        self._warnings += 1

    def _report_check(self, message: str):
        """Prints a check report using a specified message.

        Keyword arguments:
        message -- the message that describes the check
        """

        # print("\u2713 " + message)
        print(f"- {message}")
        self._checks += 1

    def _check_kind(self, doc: dict[str, str], filename: str):
        """Checks whether 'kind' is specified in the Kustomization and
        that the filename matches the kind. Reports problems if not the case.

        Keyword arguments:
        doc -- the in-memory Kustomization file dictionary
        filename -- the name of the Kustomization file
        """

        if "kind" not in doc:
            self._report_problem("missing 'kind'")
        elif "." not in filename or filename.split(".")[1] != doc['kind'].lower():
            self._report_problem(f"filename/manifest mismatch for 'kind': {doc['kind']}")

    def _check_secret_generator(self, secret_generator: list[dict[str, typing.Any]]):
        for generator in secret_generator:
            if 'name' not in generator:
                self._report_problem("secretGenerator without name")
                continue
            if 'literals' in generator:
                self._report_problem(
                    f"secretGenerator[name: {generator['name']}]: 'envs' is preferred over 'literals'")

    def _check_kustomization(
            self, doc: dict[str, typing.Any], full_filename: str, kustomize_dir: str):
        self._report_check(full_filename)

        if 'secretGenerator' in doc:
            self._check_secret_generator(doc['secretGenerator'])

        resources: list[str] = doc.get('resources', [])
        for manifest in [ x
                for x in os.listdir(kustomize_dir)
                if x != "kustomization.yaml"
                and x.endswith(".yaml")
                and x in resources]:
            self._report_problem(f"resource manifest not in resources/: {manifest}")
        if os.path.isdir(os.path.join(kustomize_dir, "resources")):
            for manifest in [ x
                    for x in os.listdir(os.path.join(kustomize_dir, "resources/")) 
                    if x.endswith(".yaml")
                    and x not in resources]:
                self._report_warning("resource manifest not listed in kustomization")

    def _check_name(self, doc: dict[str, dict[str, str]], filename: str):
        manifest_name: str = filename.split(".")[0]
        if "name" not in doc.get('metadata', {}):
            self._report_problem("missing 'name'")
        elif manifest_name != doc['metadata']['name']:
            self._report_problem(
                f"filename/manifest mismatch for 'name': {doc['metadata']['name']}")

    def _check_manifest(self, doc: dict[str, typing.Any], filename: str, full_filename: str):
        self._check_kind(doc, filename)
        self._check_name(doc, filename)

    def _check_kustomize_dir(self, kustomize_dir: str):
        self._report_check(kustomize_dir)
        kustomization_file: str = os.path.join(kustomize_dir, "kustomization.yaml")
        if not os.path.exists(kustomization_file):
            self._report_problem(f"{kustomize_dir}: kustomization.yaml not found")
            return
        self._check_resources_dir(kustomize_dir)
        self._check_patches_dir(kustomize_dir)
        with open(kustomization_file) as file:
            doc: dict[str, typing.Any] = yaml.full_load(file)
            self._check_kustomization(doc, kustomization_file, kustomize_dir)

    def _check_patches_dir(self, kustomize_dir: str):
        patches_dir: str = os.path.join(kustomize_dir, "patches")
        if os.path.isdir(patches_dir):
            self._check_dir(patches_dir)

    def _check_resources_dir(self, kustomize_dir: str):
        resources_dir: str = os.path.join(kustomize_dir, "resources")
        if os.path.isdir(resources_dir):
            self._check_dir(resources_dir)

    def _check_dir(self, cdir: str):
        self._report_check(cdir)
        for filename in os.listdir(cdir):
            full_filename: str = os.path.join(cdir, filename)
            if not filename.endswith(".yaml"):
                continue
            if filename == "kustomization.yaml":
                self._report_problem(f"{cdir}: unexpected kustomization.yaml")
                continue
            with open(full_filename) as file:
                self._report_check(f"{full_filename}:")
                try:
                    doc: dict[str, typing.Any] = yaml.full_load(file)
                    self._check_manifest(doc, filename, full_filename)
                except BaseException:
                    self._report_problem("could not parse manifest")

    def _check_kustomize_tree(self, root_dir: str):
        for current_dir, _, files in os.walk(root_dir):
            if "kustomization.yaml" in files:
                print(f"looks like a kustomize dir: {current_dir}")
                self._check_kustomize_dir(current_dir)
                print("")
