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

# Create staging area for task files
RUN mkdir -p /tmp/task-files

# Copy task files (tests, etc.) to staging area
COPY . /tmp/task-files/

# Clone pydantic repo and checkout base commit
# Use --no-cache-dir to ensure fresh clone and verify files exist
RUN rm -rf /app/pydantic-assessment && \
    git clone https://github.com/pydantic/pydantic.git /app/pydantic-assessment && \
    cd /app/pydantic-assessment && \
    git checkout 3c305a37b8f7fefc2f387d3f2f477aabe26694b0 && \
    ls -la && \
    test -f pyproject.toml || (echo "pyproject.toml not found!" && exit 1)

# Copy task test files into pydantic tests directory
RUN ls -la /app/pydantic-assessment/ && \
    cp /tmp/task-files/tests/* /app/pydantic-assessment/tests/ 2>/dev/null || true && \
    rm -rf /tmp/task-files && \
    ls -la /app/pydantic-assessment/

WORKDIR /app/pydantic-assessment

# Sync Python deps (prebuilt wheels by default; toolchain is on the path
# for tasks that opt to build pydantic-core from source).
RUN uv sync --frozen --all-extras

CMD ["bash"]
