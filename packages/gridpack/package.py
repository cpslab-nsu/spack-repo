from spack.package import *


class Gridpack(CMakePackage):
    """GridPACK is an open-source high-performance (HPC) package for simulation
    of large-scale electrical grids.  Powered by distributed (parallel)
    computing and high-performance numerical solvers, GridPACK offers several
    applications forfast simulation of electrical transmission systems.

    GridPACK includes a number of prebuilt applications that can be directly
    used.  The most commonly used and well-developed are:
      - AC Power Flow
      - Dynamics Simulation
      - Contingency Analysis

    Other applications under development or not full featured are
      - Dynamic security assessment
      - State estimation
    """

    homepage = "https://gridpack.pnnl.gov"
    url = "https://github.com/cpslab-nsu/GridPACK/archive/refs/heads/master.tar.gz"

    maintainers("ta7mid")

    version("master", sha256="90faaea85a27b4e365725b7b97775f1fb550dcdd4596a24c1ce0c16d4cb5297f")

    depends_on("cxx", type="build")
    depends_on("boost +mpi +serialization +random +filesystem +system")
    depends_on("globalarrays +cxx")
    depends_on("mpi")
    depends_on("petsc +metis +suite-sparse +superlu-dist")

    variant("shared", default=False, description="Build shared libraries")
    variant("tests", default=False, description="Build unit tests")
    variant(
        "test_timeout", default=120, description="Timeout for unit tests in seconds", when="+tests"
    )
    variant(
        "env_from_comm",
        default=False,
        description="Enable creating GridPACK environment from communicator",
        when="^globalarrays@5.9:",
    )

    root_cmakelists_dir = "src"

    def cmake_args(self):
        args = [
            "-DBoost_ROOT:PATH={}".format(self.spec["boost"].prefix),
            "-DGA_DIR:PATH={}".format(self.spec["globalarrays"].prefix),
            "-DMPI_HOME:PATH={}".format(self.spec["mpi"].prefix),
            "-DPETSC_DIR:PATH={}".format(self.spec["petsc"].prefix),
            self.define_from_variant("BUILD_SHARED_LIBS:BOOL", "shared"),
            self.define_from_variant("GRIDPACK_ENABLE_TESTS:BOOL", "tests"),
            self.define_from_variant("GRIDPACK_TEST_TIMEOUT:STRING", "test_timeout"),
            self.define_from_variant("ENABLE_ENVIRONMENT_FROM_COMM:BOOL", "env_from_comm"),
        ]

        return args
