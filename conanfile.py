from conans import ConanFile, CMake, tools
import os


class GameNetworkingSocketsConan(ConanFile):
    name = "GameNetworkingSockets"
    version = "v1.1.0"
    description = "Reliable & unreliable messages over UDP"
    topics = ("conan", "udp", "network", "networking", "internet")
    url = "https://github.com/bincrafters/conan-GameNetworkingSockets"
    homepage = "https://github.com/ValveSoftware/GameNetworkingSockets"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD 3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "conan.patch"]
    generators = "cmake"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _version = "1.1.0"
    _tag = f"v{_version}"

    requires = (
        "OpenSSL/1.1.0k@conan/stable",
        "protobuf/3.9.1@bincrafters/stable",
        "protoc_installer/3.9.1@bincrafters/stable",
    )
    build_requires = "cmake_installer/3.16.0@conan/stable"

    def source(self):
        tools.get("https://github.com/ValveSoftware/GameNetworkingSockets/archive/{}.tar.gz".format(self._tag))
        os.rename("GameNetworkingSockets-" + self._version, self._source_subfolder)
        tools.patch(self._source_subfolder, patch_file="conan.patch")

    def build(self):
        with tools.environment_append({"LD_LIBRARY_PATH": self.deps_cpp_info["protobuf"].lib_paths}):
            cmake = CMake(self)
            cmake.definitions["Protobuf_USE_STATIC_LIBS"] = not self.options["protobuf"].shared
            cmake.definitions["USE_CRYPTO25519"] = "Reference"
            cmake.configure(build_folder=self._build_subfolder)
            cmake.build(["--config", "Release"], None, "GameNetworkingSockets_s")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.pdb", dst="lib", keep_path=False)
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
        # Copy correct lib
        if self.options.shared:
            libname = "GameNetworkingSockets"
        else:
            libname = "GameNetworkingSockets_s"
        if self.settings.compiler == "Visual Studio":
            self.copy("*{}{}.lib".format(os.sep, libname), dst="lib", keep_path=False)
        else:
            self.copy("*{}lib{}.dylib".format(os.sep, libname), dst="lib", keep_path=False, symlinks=True)
            self.copy("*{}lib{}.so".format(os.sep, libname), dst="lib", keep_path=False, symlinks=True)
            self.copy("*{}lib{}.a".format(os.sep, libname), dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["STEAMDATAGRAMLIB_STATIC_LINK"]
