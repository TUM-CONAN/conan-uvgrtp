from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

class uvgRTPConan(ConanFile):

    name = "uvgrtp"
    version = "2.1.2"
    license = "Apache-2.0"
    homepage = "https://github.com/ultravideo/uvgRTP"
    url = "https://github.com/TUM-CONAN/conan-uvgrtp"
    description = "optimized rtp transport by ultravideogroup"
    topics = ("Streaming", "Network")
    settings = "os", "compiler", "build_type", "arch"
    options = {
         "shared":          [True, False],
         "with_crypto":     [True, False], 
         "fPIC": [True, False]
    }
    default_options = {
        "shared":      False,
        "with_crypto": True, 
        "fPIC": True
    }
    generators = ["cmake", "cmake_find_package"]
    exports_sources = ["patches/**","CMakeLists.txt"]
    _cmake = None

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, alias, aliased):
        content = ""
        content += textwrap.dedent("""\
            if(TARGET {aliased} AND NOT TARGET {alias})
                add_library({alias} INTERFACE IMPORTED)
                set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
            endif()
        """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join(
            "lib",
            "cmake"
        )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_folder(self):
        return "build"

    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _pkg_etc(self):
        return os.path.join(
            self.package_folder,
            "etc"
        )
    
    @property
    def _pkg_res(self):
        return os.path.join(
            self.package_folder,
            "res"
        )

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib/cmake"
        )

    @property
    def _target_aliases(self):
        aliases = {
       }
        return aliases

    def _patch_sources(self):
        for patch in []: #[{"base_path": "source_subfolder","patch_file":"patches/2.0.0-fix-cpptoml-cmake.patch"},]:
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)",
            "#install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)"
            )

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def config_options(self):
        pass
    
    def requirements(self):
        if self.options.with_crypto:
            self.requires("cryptopp/8.6.0")
    
    def validate(self):
        os = self.settings.os
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(
                "Iceoryx is just supported for Visual Studio compiler 16 and higher.")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_CRYPTO"] = "ON" if not self.options.with_crypto else "OFF"
        if self.settings.compiler != 'Visual Studio':
            self._cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self._cmake.configure()
        return self._cmake

    def source(self):
        tools.get("https://github.com/ultravideo/uvgRTP/archive/refs/tags/v%s.tar.gz" % self.version, strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.hh", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        libs = tools.collect_libs(self)
        self.cpp_info.libs = libs
