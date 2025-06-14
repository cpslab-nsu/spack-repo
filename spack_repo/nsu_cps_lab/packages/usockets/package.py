# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.makefile import MakefilePackage

from spack.package import *


class Usockets(MakefilePackage):
    """Lightweight cross-platform eventing, networking and crypto library for async applications"""

    homepage = "https://github.com/uNetworking/uSockets"
    git = "https://github.com/uNetworking/uSockets.git"

    patch("add_install_target.patch")

    maintainers("ta7mid")

    license("Apache-2.0", checked_by="ta7mid")

    version("master", branch="master", submodules=True)
    version("0.8.8", commit="833497e8e0988f7fd8d33cd4f6f36056c68d225d", submodules=True)
    version("0.8.7", commit="a15d9bbdea68fd02dab40d2394200deb1b883aa6", submodules=True)

    variant(
        "eventing",
        default="default",
        values=(
            "asio",
            "boost_asio",
            "default",
            conditional("gcd", when="platform=darwin"),
            conditional("io_uring", when="platform=linux"),
            "libuv",
        ),
        description=(
            'Event notification library/implementation to use for asynchronous I/O; "default" '
            "resolves to libuv on Windows, epoll syscalls on Linux, and kqueue syscalls on Darwin "
            "and FreeBSD"
        )
    )
    variant(
        "ssl",
        default="none",
        values=(
            "none",
            "boringssl",
            "openssl",
            # "wolfssl",  # TODO: soruce not distributed with uSockets and no Spack package
        ),
        description='SSL/TLS library to use, or "none" for no SSL or TLS support',
    )
    variant(
        "debug",
        default=False,
        description="Build with debug symbols and without optimizations"
    )
    variant("asan", default=False, description="Enable AddressSanitizer")

    # https://github.com/uNetworking/uSockets/issues/111#issuecomment-899169739
    with when("ssl=boringssl"):
        variant("lsquic", default=False, description="Enable QUIC support via LiteSpeed QUIC")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("gmake", type="build")
    depends_on("liburing", when="eventing=io_uring")
    depends_on("libuv", when="eventing=libuv")
    depends_on("libuv", when="eventing=default platform=windows")
    depends_on("boringssl~shared", when="ssl=boringssl")
    depends_on("openssl@1.1:", when="ssl=openssl")
    depends_on("lsquic~shared", when="+lsquic")

    # TODO
    # https://github.com/uNetworking/uSockets/blob/182b7e4fe7211f98682772be3df89c71dc4884fa/Makefile#L80
    # indicates that cxxstd=14 is required
    depends_on("asio cxxstd=14", when="eventing=asio")
    depends_on("boost cxxstd=14", when="eventing=boost_asio")

    # TODO: package WolfSSL
    # depends_on("wolfssl", when="ssl=wolfssl")

    build_targets: list[str] = ["default"]

    def edit(self, pkg, spec):
        makefile = FileFilter("Makefile")
        usockets_h = FileFilter("src/libusockets.h")

        makefile.filter("-lstdc++", "")

        ev = self.spec.variants["eventing"].value
        regex = r"^(/\* Decide what eventing system)"
        if ev == "io_uring":
            makefile.filter("/usr/lib/liburing.a", f"'{spec["liburing"].prefix.lib}/liburing.a'")
            usockets_h.filter(regex, "/* injected by Spack */\n#define LIBUS_USE_IO_URING\n\n\\1")
        elif ev == "libuv":
            usockets_h.filter(regex, "/* injected by Spack */\n#define LIBUS_USE_LIBUV\n\n\\1")
        elif ev == "gcd":
            usockets_h.filter(regex, "/* injected by Spack */\n#define LIBUS_USE_GCD\n\n\\1")
        elif ev in ("asio", "boost_asio"):
            usockets_h.filter(regex, "/* injected by Spack */\n#define LIBUS_USE_ASIO\n\n\\1")

        if "ssl=boringssl" in spec:
            pref = spec["boringssl"].prefix
            makefile.filter("-Iboringssl/include", f"'-I{pref.include}'")
            makefile.filter("boringssl/build/ssl/libssl.a", f"'{pref.lib}/libssl.a'")
            makefile.filter("boringssl/build/crypto/libcrypto.a", f"'{pref.lib}/libcrypto.a'")

        if "+lsquic" in spec:
            pref = self.spec["lsquic"].prefix
            makefile.filter("-Ilsquic/include", f"'-I{pref.include}'")
            makefile.filter("lsquic/src/liblsquic/liblsquic.a", f"'{pref.lib}/liblsquic.a'")

        if "+debug" in spec:
            makefile.filter("-O3", "-O0 -g")

    def setup_build_environment(self, env) -> None:
        env.set("DESTDIR", self.prefix)

        ev = self.spec.variants["eventing"].value
        if ev == "io_uring":
            env.set("WITH_IO_URING", "1")
        elif ev == "libuv":
            env.set("WITH_LIBUV", "1")
        elif ev == "gcd":
            env.set("WITH_GCD", "1")
        elif ev in ("asio", "boost_asio"):
            env.set("WITH_ASIO", "1")

        ssl = self.spec.variants["ssl"].value
        if ssl == "boringssl":
            env.set("WITH_BORINGSSL", "1")
        elif ssl == "openssl":
            env.set("WITH_OPENSSL", "1")

        if "+asan" in self.spec:
            env.set("WITH_ASAN", "1")

        if "+lsquic" in self.spec:
            env.set("WITH_QUIC", "1")
