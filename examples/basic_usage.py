"""Basic usage example — demonstrates the public API end-to-end.

Run with:
    python examples/basic_usage.py
"""

from constitution_overlay import Constitution, PolicyReject, halt_on_reject

# -- 1. Base constitution (human-written per-project file) --------------------

BASE: dict = {
    "business": {
        "legal_name": "Arnold Wender",
        "home_address": {
            "streetAddress": "Franckestrasse 3a",
            "addressLocality": "Halle (Saale)",
            "postalCode": "06110",
            "addressCountry": "DE",
        },
    },
    "brand": {
        "prohibited_terms": ["billig", "guenstigster"],
    },
    "limits": {
        "max_files_per_commit": 50,
        "no_force_push": True,
    },
}

# -- 2. Corrections overlay (situational override for this run) ---------------
# A later layer overrides earlier ones (Kustomize rightmost-wins semantics).

CORRECTIONS: dict = {
    "limits": {
        "max_files_per_commit": 200,  # this repo commits large batches
    },
}

# -- 3. Build the merged constitution -----------------------------------------

constitution = Constitution.from_layers(BASE, CORRECTIONS)

print("Merged constitution:")
print(f"  legal_name           : {constitution.get('business.legal_name')}")
print(f"  addressLocality      : {constitution.get('business.home_address.addressLocality')}")
print(f"  max_files_per_commit : {constitution.get('limits.max_files_per_commit')}")
print(f"  no_force_push        : {constitution.get('limits.no_force_push')}")

# -- 4. Enforce rules executor-side (not via prompt) --------------------------


@halt_on_reject(constitution)
def commit_files(files: list[str]) -> None:
    limit = constitution.get("limits.max_files_per_commit")
    if len(files) > limit:
        raise PolicyReject(f"too many files: {len(files)} > {limit}")
    print(f"  committed {len(files)} files")


@halt_on_reject(constitution)
def write_copy(text: str) -> None:
    prohibited = constitution.get("brand.prohibited_terms", [])
    hits = [t for t in prohibited if t in text.lower()]
    if hits:
        raise PolicyReject(f"prohibited brand terms in copy: {hits}")
    print(f"  copy approved: {text!r}")


print("\nTest: commit within limit (10 files) — should pass")
commit_files([f"file{i}.py" for i in range(10)])

print("\nTest: commit over limit (300 files) — should reject")
try:
    commit_files([f"file{i}.py" for i in range(300)])
except PolicyReject as e:
    print(f"  halted: {e}")

print("\nTest: clean copy — should pass")
write_copy("Professionelle Webentwicklung in Halle (Saale)")

print("\nTest: prohibited term — should reject")
try:
    write_copy("Der billigste Webdesigner in Halle")
except PolicyReject as e:
    print(f"  halted: {e}")


if __name__ == "__main__":
    pass  # all code runs at module level above for simplicity
