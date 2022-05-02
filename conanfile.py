from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

class uvgRTPConan(ConanFile):

    name = "uvgrtp"
    version = "2.0.1"
    license = "Apache-2.0"
    homepage = "https://github.com/ultravideo/uvgRTP"
    url = "https://github.com/TUM-CONAN/conan-uvgrtp"
    description = "optimized rtp transport by ultravideogroup"
    topics = ("Streaming", "Network")
    settings = "os", "compiler", "build_type", "arch"
    options = {
         "shared":          [True, False],
         "with_crypto":     [True, False]
    }
    default_options = {
        "shared":      False,
        "with_crypto": True
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
            # "uvgrtp::uvgrtp": "iceoryx::posh",
            # "iceoryx_posh::iceoryx_posh_roudi": "iceoryx::posh_roudi",
            # "iceoryx_binding_c::iceoryx_binding_c": "iceoryx::binding_c",
            # "iceoryx_hoofs::iceoryx_hoofs": "iceoryx::hoofs",
        }
        return aliases

    def _patch_sources(self):
        for patch in []: #[{"base_path": "source_subfolder","patch_file":"patches/2.0.0-fix-cpptoml-cmake.patch"},]:
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)",
            "#install(FILES ${CMAKE_CURRENT_BINARY_DIR}/uvgrtp.pc DESTINATION ${PKG_CONFIG_PATH}/)"
            )

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
        # if os == "Windows" and self.options.shared:
        #     raise ConanInvalidConfiguration(
        #         'Using Iceoryx on Windows currently just possible with "shared=False"')
        # if (compiler == "gcc" or compiler == "clang") and compiler.libcxx != "libstdc++11":
        #     raise ConanInvalidConfiguration(
        #         'Using Iceoryx with gcc or clang on Linux requires "compiler.libcxx=libstdc++11"')
        # if os == "Linux" and compiler == "gcc" and version <= "5":
        #     raise ConanInvalidConfiguration(
        #         "Using Iceoryx with gcc on Linux requires gcc 6 or higher.")
        # if os == "Linux" and compiler == "gcc" and version == "6":
        #     self.output.warn(
        #         "Iceoryx package is compiled with gcc 6, it is recommended to use 7 or higher")
        #     self.output.warn(
        #         "GCC 6 will built with warnings.")
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(
                "Iceoryx is just supported for Visual Studio compiler 16 and higher.")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_CRYPTO"] = "ON" if not self.options.with_crypto else "OFF"
        self._cmake.configure()
        return self._cmake

    def source(self):
        # tools.get("https://github.com/ultravideo/uvgRTP/archive/refs/tags/v%s.tar.gz" % self.version, strip_root=True,
        #           destination=self._source_subfolder)
        tools.get("https://github.com/ultravideo/uvgRTP/archive/refs/heads/master.tar.gz", strip_root=True,
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
        # self.copy("*.cmake", src=os.path.join(self._source_subfolder, "iceoryx_hoofs", "cmake"), dst="cmake")
        # tools.rmdir(self._pkg_share)
        # tools.rmdir(self._pkg_cmake)
        # tools.mkdir(self._pkg_res)
        # tools.rmdir(self._pkg_etc)
        # for alias, aliased in self._target_aliases.items():
        #     cmake_file = "conan-official-{}-targets.cmake".format(
        #         aliased.replace("::", "_")
        #     )
        #     self._create_cmake_module_alias_targets(
        #         os.path.join(
        #             self.package_folder,
        #             self._module_subfolder,
        #             cmake_file
        #         ),
        #         alias,
        #         aliased
        #     )

    def package_info(self):
        libs = tools.collect_libs(self)
        self.cpp_info.libs = libs

        # self.cpp_info.names["cmake_find_package"] = "iceoryx"
        # self.cpp_info.names["cmake_find_multi_package"] = "iceoryx"
        # # platform component
        # self.cpp_info.components["platform"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["platform"].name = "platform"
        # self.cpp_info.components["platform"].libs = ["iceoryx_platform"]
        # if self.settings.os in ["Linux","Macos","Neutrino"]:
        #     self.cpp_info.components["platform"].system_libs.append("pthread")
        # # hoofs component
        # self.cpp_info.components["hoofs"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["hoofs"].name = "hoofs"
        # self.cpp_info.components["hoofs"].libs = ["iceoryx_hoofs"]
        # self.cpp_info.components["hoofs"].requires = ["platform"]
        # if self.settings.os == "Linux":
        #     self.cpp_info.components["hoofs"].requires.append("acl::acl")
        #     self.cpp_info.components["hoofs"].system_libs.append("rt")
        # if self.settings.os in ["Linux","Macos","Neutrino"]:
        #     self.cpp_info.components["hoofs"].system_libs.append("pthread")
        # if self.settings.os == "Linux":
        #     self.cpp_info.components["hoofs"].system_libs.append("atomic")
        # self.cpp_info.components["hoofs"].builddirs = self._pkg_cmake
        # self.cpp_info.components["hoofs"].build_modules["cmake_find_package"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_hoofs-targets.cmake")
        # ]
        # self.cpp_info.components["hoofs"].build_modules["cmake_find_package_multi"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_hoofs-targets.cmake")
        # ]
        # # posh component 
        # self.cpp_info.components["posh"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["posh"].name = "posh"
        # self.cpp_info.components["posh"].libs = ["iceoryx_posh"]
        # self.cpp_info.components["posh"].requires = ["hoofs"]
        # if self.settings.os in ["Linux","Macos","Neutrino"]:
        #     self.cpp_info.components["posh"].system_libs.append("pthread")
        # self.cpp_info.components["posh"].builddirs = self._pkg_cmake
        # self.cpp_info.components["posh"].build_modules["cmake_find_package"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_posh-targets.cmake")
        # ]
        # self.cpp_info.components["posh"].build_modules["cmake_find_package_multi"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_posh-targets.cmake")
        # ]
        # # roudi component
        # self.cpp_info.components["posh_roudi"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["posh_roudi"].name = "posh_roudi"
        # self.cpp_info.components["posh_roudi"].libs = ["iceoryx_posh_roudi"]
        # self.cpp_info.components["posh_roudi"].requires = ["hoofs", "posh"]
        # if self.options.toml_config:
        #     self.cpp_info.components["post_roudi"].requires.append("cpptoml::cpptoml")
        # if self.settings.os in ["Linux","Macos","Neutrino"]:
        #     self.cpp_info.components["posh_roudi"].system_libs.append("pthread")
        # self.cpp_info.components["posh_roudi"].builddirs = self._pkg_cmake
        # self.cpp_info.components["posh_roudi"].build_modules["cmake_find_package"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_posh_roudi-targets.cmake")
        # ]
        # self.cpp_info.components["posh_roudi"].build_modules["cmake_find_package_multi"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_posh_roudi-targets.cmake")
        # ]
        # # posh config component 
        # self.cpp_info.components["posh_config"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["posh_config"].name = "posh_config"
        # self.cpp_info.components["posh_config"].libs = ["iceoryx_posh_config"]
        # self.cpp_info.components["posh_config"].requires = ["posh_roudi", "hoofs", "posh"]
        # if self.settings.os in ["Linux","Macos","Neutrino"]:
        #     self.cpp_info.components["posh_config"].system_libs.extend(["pthread"])
        # # posh gw component
        # self.cpp_info.components["posh_gw"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["posh_gw"].name = "posh_gw"
        # self.cpp_info.components["posh_gw"].libs = ["iceoryx_posh_gateway"]
        # self.cpp_info.components["posh_gw"].requires = ["hoofs", "posh"]
        # # bind_c component
        # self.cpp_info.components["bind_c"].includedirs.append('include/iceoryx/v%s' % self.version)
        # self.cpp_info.components["bind_c"].name = "binding_c"
        # self.cpp_info.components["bind_c"].libs = ["iceoryx_binding_c"]
        # self.cpp_info.components["bind_c"].requires = ["hoofs", "posh"]
        # if self.settings.os in ["Linux","Macos","Neutrino"]:        
        #     self.cpp_info.components["bind_c"].system_libs.extend(["pthread", "stdc++"])
        # self.cpp_info.components["bind_c"].builddirs = self._pkg_cmake
        # self.cpp_info.components["bind_c"].build_modules["cmake_find_package"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_binding_c-targets.cmake")
        # ]
        # self.cpp_info.components["bind_c"].build_modules["cmake_find_package_multi"] = [
        #     os.path.join(self._module_subfolder, "conan-official-iceoryx_binding_c-targets.cmake")
        # ]
        # if self.options.with_introspection and self.settings.os != "Windows":
        #     # introspection
        #     self.cpp_info.components["introspection"].name = "introspection"
        #     self.cpp_info.components["introspection"].libs = ["iceoryx_introspection"]
        #     self.cpp_info.components["introspection"].requires = ["hoofs", "posh", "ncurses::ncurses"]
