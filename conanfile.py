from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import load, update_conandata, copy, replace_in_file, collect_libs, get
import os

class uvgRTPConan(ConanFile):

    name = "uvgrtp"
    version = "2.3.0"
    license = "Apache-2.0"

    homepage = "https://github.com/ultravideo/uvgRTP"
    url = "https://github.com/TUM-CONAN/conan-uvgrtp"
    description = "optimized rtp transport by ultravideogroup"
    topics = ("Streaming", "Network")

    settings = "os", "compiler", "build_type", "arch"
    options = {
         "shared": [True, False],
         "with_crypto": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "with_crypto": False,
        "fPIC": True
    }

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)",
            "#install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)"
            )

    def requirements(self):
        if self.options.with_crypto:
            self.requires("cryptopp/8.7.0")
    
    def source(self):
        get(self,
            "https://github.com/ultravideo/uvgRTP/archive/refs/tags/v%s.tar.gz" % self.version,
            strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # XXX recognition of libcrypto++ does not seem to work - it's using pkg_config from within cmake, not find_package
        tc.cache_variables["DISABLE_CRYPTO"] = not self.options.with_crypto
        tc.cache_variables["PKG_CONFIG_PATH"] = os.path.join(self.package_folder, "pkgconfig")

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # self.copy("*.hh", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
