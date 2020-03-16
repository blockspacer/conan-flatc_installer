from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment, RunEnvironment
from conans.errors import ConanInvalidConfiguration, ConanException
from conans.tools import os_info
import os, re, stat, fnmatch, platform, glob
from functools import total_ordering

class FlatcConan(ConanFile):
    name = "flatc_conan"
    version = "v1.11.0"
    flatbuffers_dep_version = "1.11.0"
    url = "https://CHANGE_ME"
    repo_url = 'https://github.com/google/flatbuffers.git'
    homepage = "https://github.com/google/flatbuffers"
    topics = ("flatbuffers", "flatbuffers compiler", "serialization", "rpc")
    author = "CHANGE_ME <>"
    description = ("flatc is a compiler for flatbuffers schema files. It can "
                   "generate among others C++, Java and Python code.")
    license = "BSD-3-Clause" # CHANGE_ME
    exports = ["LICENSE.txt"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_paths", "virtualenv"#, "cmake_find_package_multi"
    settings = "os_build", "os", "arch", "compiler", "build_type", "arch_build"
    #short_paths = True
    options = {
        # "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }

    @property
    def _source_dir(self):
        return "source_subfolder"

    @property
    def _build_dir(self):
        return "."

    def source(self):
        #sha256 = "3f4a286642094f45b1b77228656fbd7ea123964f19502f9ecfd29933fd23a50b"
        #tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        #os.rename("flatbuffers-%s" % self.version, self._source_subfolder)
        self.run('git clone --progress --depth 1 --branch {} {} {}'.format(self.version, self.repo_url, self._source_dir))

    def requirements(self):
        self.requires.add("flatbuffers/{}@google/stable".format(self.flatbuffers_dep_version), private=True)
        #self.requires("protobuf/v3.9.1@conan/stable")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = False
        cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        cmake.definitions["FLATBUFFERS_INSTALL"] = True
        cmake.configure(build_folder=self._build_dir)
        return cmake

    def build(self):
        self.output.info('Building package \'{}\''.format(self.name))

        # NOTE: make sure `protoc` can be found using PATH environment variable
        bin_path = ""
        for p in self.deps_cpp_info.bin_paths:
            bin_path = "%s%s%s" % (p, os.pathsep, bin_path)

        lib_path = ""
        for p in self.deps_cpp_info.lib_paths:
            lib_path = "%s%s%s" % (p, os.pathsep, lib_path)

        # NOTE: make sure `/lib` from `protobuf` can be found using PATH environment variable
        #for p in self.deps_cpp_info["protobuf"].lib_paths:
        #    lib_path = "%s%s%s" % (p, os.pathsep, lib_path)
        #    self.output.info('protobuf lib_path += %s' % (p))
        #    files = [f for f in glob.glob(p + "/**", recursive=True)]
        #    for f in files:
        #        self.output.info('protobuf libs: %s' % (f))

        include_path = ""
        for p in self.deps_cpp_info.includedirs:
            include_path = "%s%s%s" % (p, os.pathsep, include_path)

        # NOTE: make sure `/include` from `protobuf` can be found using PATH environment variable
        #for p in self.deps_cpp_info["protobuf"].include_paths:
        #    include_path = "%s%s%s" % (p, os.pathsep, include_path)

        # see https://docs.conan.io/en/latest/reference/build_helpers/autotools.html
        # AutoToolsBuildEnvironment sets LIBS, LDFLAGS, CFLAGS, CXXFLAGS and CPPFLAGS based on requirements
        env_build = AutoToolsBuildEnvironment(self)
        self.output.info('AutoToolsBuildEnvironment include_paths = %s' % (','.join(env_build.include_paths)))

        env = {
             "LIBS": "%s%s%s" % (env_build.vars["LIBS"] if "LIBS" in env_build.vars else "", " ", os.environ["LIBS"] if "LIBS" in os.environ else ""),
             "LDFLAGS": "%s%s%s" % (env_build.vars["LDFLAGS"] if "LDFLAGS" in env_build.vars else "", " ", os.environ["LDFLAGS"] if "LDFLAGS" in os.environ else ""),
             "CFLAGS": "%s%s%s" % (env_build.vars["CFLAGS"] if "CFLAGS" in env_build.vars else "", " ", os.environ["CFLAGS"] if "CFLAGS" in os.environ else ""),
             "CXXFLAGS": "%s%s%s" % (env_build.vars["CXXFLAGS"] if "CXXFLAGS" in env_build.vars else "", " ", os.environ["CXXFLAGS"] if "CXXFLAGS" in os.environ else ""),
             "CPPFLAGS": "%s%s%s" % (env_build.vars["CPPFLAGS"] if "CPPFLAGS" in env_build.vars else "", " ", os.environ["CPPFLAGS"] if "CPPFLAGS" in os.environ else ""),
             "PATH": "%s%s%s%s%s" % (bin_path, os.pathsep, include_path, os.pathsep, os.environ["PATH"] if "PATH" in os.environ else ""),
             "LD_LIBRARY_PATH": "%s%s%s" % (lib_path, os.pathsep, os.environ["LD_LIBRARY_PATH"] if "LD_LIBRARY_PATH" in os.environ else "")
        }

        self.output.info("=================linux environment for %s=================\n" % (self.name))
        self.output.info('PATH = %s' % (env['PATH']))
        self.output.info('LD_LIBRARY_PATH = %s' % (env['LD_LIBRARY_PATH']))
        self.output.info('')
        with tools.environment_append(env):
            with tools.chdir(self._source_dir):
                cmake = self._configure_cmake()
                cmake.build()

    def package(self):
        self.output.info('Packaging package \'{}\''.format(self.name))

        self.copy("LICENSE", dst="licenses", src=self._source_dir)
        self.copy("*FlatBuffers*", dst="", src=os.path.join(self._source_dir,"CMake"))

        self.output.info('Packaging package \'{}\''.format(self.name))

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('*', dst='include', src='{}/include'.format(self._source_dir))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self._build_dir), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        #self.copy("*", dst="bin", src="bin")
        #self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

        self.copy("*", dst="bin", src='{}/javascript/net/grpc/web'.format(self._source_dir))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        self.info.include_build_settings()

    def package_info(self):
        self.cpp_info.includedirs = ['{}/include'.format(self.package_folder)]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "lib"))
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        # collects libupb, make sure to remove 03-simple.a
        self.cpp_info.libs = tools.collect_libs(self)

        for libpath in self.deps_cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(libpath)

        self.env_info.FlatBuffers_ROOT = self.package_folder
        flatc = "flatc.exe" if self.settings.os_build == "Windows" else "flatc"
        self.env_info.FLATC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", flatc))

        self.cpp_info.names["cmake_find_package"] = "flatc"
        self.cpp_info.names["cmake_find_package_multi"] = "flatc"
