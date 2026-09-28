#!/usr/bin/env python3
"""Minimal client for the PubMLST REST API.

Depends on the standard library only, so processes that import it do not need
extra packages in their Conda environment.

Two assumptions that hold for common schemes but not in general, and which this
module resolves dynamically instead:

  * The MLST scheme is not always `schemes/1`. Of the 135 PubMLST schemes that
    define ST profiles, seven use another id (Salmonella uses 2).
    `detect_mlst_scheme()` finds it by description.
  * Schemes do not always have seven loci; they range from 2 to 10. The locus
    list is always read from the scheme definition.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://rest.pubmlst.org"

# PubMLST data access key. Without it the API serves only data deposited up to
# 31 December 2024; newer alleles and STs require an account. The key is read
# from the environment, where Nextflow places it from its secrets store, so it
# never appears in the code, the command line or the task work directory.
API_KEY_ENV = "PUBMLST_API_KEY"


class AuthenticationError(RuntimeError):
    """The API key was rejected. Retrying cannot fix this."""


def authenticated():
    """True when a data access key is available."""
    return bool(os.environ.get(API_KEY_ENV, "").strip())


def _headers():
    key = os.environ.get(API_KEY_ENV, "").strip()
    return {"X-API-Key": key} if key else {}


# Retry policy for brief outages and transient 5xx responses from PubMLST.
ATTEMPTS = 5
BACKOFF_BASE = 5
TIMEOUT = 120


def _get(url, binary=False):
    """GET with retries and linear backoff. Re-raises once attempts run out."""
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            request = urllib.request.Request(url, headers=_headers())
            with urllib.request.urlopen(request, timeout=TIMEOUT) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            # 404 means the resource does not exist; retrying cannot help.
            if e.code == 404:
                raise
            # 401/403 means the key was rejected; retrying cannot help either.
            if e.code in (401, 403):
                raise AuthenticationError(
                    f"PubMLST rejected the API key (HTTP {e.code}). Check the key "
                    f"stored with 'nextflow secrets set {API_KEY_ENV}'.") from e
            last_error = e
        except Exception as e:
            last_error = e
        if attempt < ATTEMPTS:
            delay = BACKOFF_BASE * attempt
            print(f"[WARN] Request to {url} failed (attempt {attempt}/{ATTEMPTS}): "
                  f"{last_error}. Retrying in {delay}s...", file=sys.stderr)
            time.sleep(delay)
    raise RuntimeError(f"Could not fetch {url} after {ATTEMPTS} attempts: {last_error}")


def get_json(url):
    return json.loads(_get(url))


def get_text(url):
    return _get(url)


def resolve_db(species):
    """Accept 'sagalactiae' or 'pubmlst_sagalactiae_seqdef'; return the full name."""
    species = species.strip()
    if species.startswith("pubmlst_") and species.endswith("_seqdef"):
        return species
    return f"pubmlst_{species}_seqdef"


def short_name(db):
    """Inverse of resolve_db: 'pubmlst_sagalactiae_seqdef' -> 'sagalactiae'."""
    if db.startswith("pubmlst_") and db.endswith("_seqdef"):
        return db[len("pubmlst_"):-len("_seqdef")]
    return db


def list_seqdef_databases():
    """Return [(db_name, description)] for every seqdef database in PubMLST."""
    groups = get_json(f"{BASE_URL}/db")
    databases = []
    for group in groups:
        for db in group.get("databases", []):
            if db["name"].endswith("_seqdef"):
                databases.append((db["name"], db["description"]))
    return sorted(set(databases))


def detect_mlst_scheme(db, scheme_id=None):
    """Return the full scheme record for the MLST scheme of a seqdef database.

    An explicit `scheme_id` is used as given. Otherwise the scheme whose
    description starts with 'MLST' is selected, rather than assuming id 1.
    """
    if scheme_id is not None:
        scheme = get_json(f"{BASE_URL}/db/{db}/schemes/{scheme_id}")
        scheme["_id"] = str(scheme_id)
        return scheme

    listing = get_json(f"{BASE_URL}/db/{db}/schemes")
    for s in listing.get("schemes", []):
        if s["description"].strip().upper().startswith("MLST"):
            scheme = get_json(s["scheme"])
            scheme["_id"] = s["scheme"].rstrip("/").split("/")[-1]
            return scheme
    raise RuntimeError(
        f"Database '{db}' publishes no MLST scheme. "
        f"Run --list_species to see the supported species."
    )


def scheme_loci(scheme):
    """Locus names of the scheme, in the order PubMLST publishes them."""
    return [u.rstrip("/").split("/")[-1] for u in scheme.get("loci", [])]


def has_profiles(scheme):
    """True when the scheme defines STs, which is required to assign one."""
    return bool(scheme.get("primary_key_field"))
