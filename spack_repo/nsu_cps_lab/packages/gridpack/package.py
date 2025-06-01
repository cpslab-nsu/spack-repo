from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Gridpack(CMakePackage):
    """GridPACK is an open-source HPC package for simulation of large-scale electrical grids.
    Powered by distributed (parallel) computing and high-performance numerical solvers, it offers
    several applications for fast simulation of electrical transmission systems, as well as the
    building blocks for developing custom simulation applications.  The most mature and commonly
    used of the pre-built applications include the AC Power Flow, Dynamics Simulation, and
    Contingency Analysis applications.  Notable among other applications, which are not yet fully
    featured, are Dynamic Security Assessment and State Estimation.
    """

    homepage = "https://gridpack.pnnl.gov"
    url = "https://github.com/cpslab-nsu/GridPACK/archive/refs/heads/master.tar.gz"

    maintainers("ta7mid")

    version("master", sha256="90faaea85a27b4e365725b7b97775f1fb550dcdd4596a24c1ce0c16d4cb5297f")

    variant("shared", default=False, description="Build dynamically linked libraries")
    variant("tests", default=False, description="Enable build of unit tests")
    variant(
        "test_timeout",
        default="120",
        description="Timeout for unit tests in seconds",
        when="+tests",
    )

    # https://github.com/GridOPTICS/GridPACK/pull/229#pullrequestreview-2679229691
    variant(
        "env_from_comm",
        default=False,
        description="Enable creating GridPACK environment from communicator",
        when="^globalarrays@5.9:",
    )

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("boost+mpi+serialization+random+filesystem+system")
    depends_on("globalarrays+cxx")
    depends_on("mpi")
    depends_on("petsc+metis+suite-sparse")

    # https://github.com/GridOPTICS/GridPACK/blob/03d41de9114e4781f1c6ac42ee0410822a0c8a4e/docs/markdown/required/PARMETIS.md?plain=1#L21
    depends_on("parmetis@4:")

    root_cmakelists_dir = "src"

    def cmake_args(self):
        return [
            self.define("Boost_ROOT:", self.spec["boost"].prefix),
            self.define("GA_DIR", self.spec["globalarrays"].prefix),
            self.define("MPI_C_COMPILER", self.spec["mpi"].mpicc),
            self.define("MPI_CXX_COMPILER", self.spec["mpi"].mpicxx),
            self.define("PETSC_DIR", self.spec["petsc"].prefix),
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("GRIDPACK_ENABLE_TESTS", "tests"),
            self.define_from_variant("GRIDPACK_TEST_TIMEOUT", "test_timeout"),
            self.define_from_variant("ENABLE_ENVIRONMENT_FROM_COMM", "env_from_comm"),
        ]

    def setup_run_environment(self, env):
        env.set("GRIDPACK_DIR", self.prefix)
