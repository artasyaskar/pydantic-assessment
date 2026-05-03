ARG RUST_TOOLCHAIN=1.90.0
FROM rust:${RUST_TOOLCHAIN}-bookworm AS rust-base

FROM python:3.11-bookworm

# Pinned Rust toolchain so candidates can rebuild pydantic-core or any
# other Rust extension from source.
COPY --from=rust-base /usr/local/cargo /usr/local/cargo
COPY --from=rust-base /usr/local/rustup /usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:${PATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        pkg-config \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv pinned by image tag.
COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /usr/local/bin/

# maturin pinned for any local Rust extension builds.
RUN pip install --no-cache-dir maturin==1.7.4

# Reduce peak memory during the Rust compile so the build stays within
# its CPU/memory budget.
ENV CARGO_BUILD_JOBS=1
ENV RUSTFLAGS="-C codegen-units=1 -C debuginfo=0"

WORKDIR /app/pydantic-assessment
COPY . /app/pydantic-assessment

# Initialize git history at the workdir. Idempotent so the same Dockerfile
# works in two contexts:
#   - silver-k8s-api kaniko build (`.git/` is stripped from the build context
#     by workers/silver-k8s-api/build.py, so we initialize fresh).
#   - candidate local `docker build .` (`.git/` ships in the assessment .zip
#     pointing at pydantic.git, so we keep the existing repo).
#
# Fetches ALL branches and tags from upstream so per-task
# `git reset --hard <base_commit>` works for any commit a candidate picks
# from the silver repoGitHistories doc, including commits on release
# branches like v2.13-fixes that aren't reachable from main.
RUN { [ -d .git ] || git init . ; } \
 && { git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/pydantic/pydantic.git ; } \
 && git remote set-url origin https://github.com/pydantic/pydantic.git \
 && git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/tags/*:refs/tags/*' \
 && git reset --soft refs/remotes/origin/main

# Sync Python deps (prebuilt wheels by default; toolchain is on the path
# for tasks that opt to build pydantic-core from source).
RUN uv sync --frozen --all-extras

CMD ["bash"]
