# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.makefile import MakefilePackage

from spack.package import *


class Uwebsockets(MakefilePackage):
    """uWebSockets is a simple, secure & standards compliant web server for HTTP and WebSocket
    applications."""

    homepage = "https://github.com/uNetworking/uWebSockets"
    url = "https://github.com/uNetworking/uWebSockets/archive/refs/tags/v20.74.0.tar.gz"

    maintainers("ta7mid")

    license("Apache-2.0", checked_by="ta7mid")

    version("20.74.0", sha256="e1d9c99b8e87e78a9aaa89ca3ebaa450ef0ba22304d24978bb108777db73676c")
    version("20.73.0", sha256="44c18b752991d390f29a96067fc7fe682185fce87f725872de87c90e4bce07ef")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("usockets", type="run")
    depends_on("libdeflate", type="run")
    depends_on("zlib", type="run")

    def edit(self, pkg, spec):
        makefile = FileFilter("GNUmakefile")
        makefile.filter("/usr/local", self.prefix)

    def build(self, pkg, spec):
        # it's a header-only library, so no build step is needed
        pass
