# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Usockets(CMakePackage):
    """Miniscule cross-platform eventing, networking & crypto for async applications"""

    homepage = "https://github.com/uNetworking/uSockets"
    url = "https://github.com/uNetworking/uSockets/archive/refs/tags/v0.8.8.tar.gz"
    patch("add_cmake_support.patch")

    maintainers("ta7mid")

    license("Apache-2.0", checked_by="ta7mid")

    version("0.8.8", sha256="d14d2efe1df767dbebfb8d6f5b52aa952faf66b30c822fbe464debaa0c5c0b17")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    variant(
        "ssl",
        default="none",
        values=("none", "openssl", "boringssl", "wolfssl"),
        description="SSL implementation",
    )
    depends_on("openssl", when="ssl=openssl")
    # depends_on("boringssl", when="ssl=boringssl")  # TODO: create boringssl
    # depends_on("wolfssl", when="ssl=wolfssl")  # TODO: create wolfssl

    variant(
        "eventloop",
        default="syscall",
        values=("syscall", "liburing", "libuv", "asio", "libdispatch"),
        description="Event loop implementation",
    )
    depends_on("liburing", when="eventloop=liburing")
    depends_on("libuv", when="eventloop=libuv")
    depends_on("asio", when="eventloop=asio")
    # depends_on("libdispatch", when="eventloop=libdispatch")  # TODO: create libdispatch

    variant("asan", default=False, description="Enable AddressSanitizer")

    requires(
        "eventloop=libuv",
        when="platform=windows",
        msg="libuv is the only supported event loop implementation on Windows",
    )

    def cmake_args(self):
        args = [self.define("WITH_OPENSSL", self.spec.variants["ssl"].value == "openssl")]
        return args

    @property
    def libs(self):
        return find_libraries("libu?ockets", root=self.prefix.lib, shared=False)
