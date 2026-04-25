"""Basic usage example.

[TODO] this example will run end-to-end once v0.1 is implemented.
"""

# from constitution_overlay import Constitution, halt_on_reject, PolicyReject
#
# base = {
#     "rules": {
#         "no_force_push": True,
#         "max_files_per_commit": 50,
#     }
# }
#
# overlay = {
#     "rules": {
#         # Local override: this repo allows up to 200 files per commit.
#         "max_files_per_commit": 200,
#     }
# }
#
# c = Constitution.from_layers(base, overlay)
#
#
# @halt_on_reject(c)
# def commit_files(files: list[str]) -> None:
#     limit = c.get("rules.max_files_per_commit")
#     if len(files) > limit:
#         raise PolicyReject(f"too many files: {len(files)} > {limit}")
#     print(f"committing {len(files)} files")
#
#
# if __name__ == "__main__":
#     commit_files(["a.py", "b.py"])  # ok
#     try:
#         commit_files([f"f{i}.py" for i in range(300)])
#     except PolicyReject as e:
#         print(f"halted: {e}")
