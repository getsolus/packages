//
// Copyright © 2021 Solus Project
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

package main

import (
	"archive/tar"
	"bytes"
	"fmt"
	"github.com/DataDrake/abi-wizard/abi"
	log "github.com/DataDrake/waterlog"
	"github.com/DataDrake/waterlog/format"
	"github.com/DataDrake/waterlog/level"
	"github.com/getsolus/libeopkg/archive"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

func removeTemp(temp string) {
	if err := os.RemoveAll(temp); err != nil {
		log.Fatalf("Failed to remove temp dir '%s', reason: %s\n", temp, err)
	}
}

func AddPackage(r abi.Report, path string) {
	log.Infof("Scanning '%s'...\n", path)
	pkg, err := archive.Open(path)
	if err != nil {
		log.Fatalf("Failed to open package '%s', reason: %s\n", path, err)
	}
	temp, err := ioutil.TempDir(os.TempDir(), "yabi")
	if err != nil {
		log.Fatalf("Failed to create temp directory, reason: %s\n", err)
	}
	defer removeTemp(temp)
	log.Debugf("Created temp directory '%s'\n", temp)
	if err = pkg.ExtractTarball(temp); err != nil {
		log.Fatalf("Failed to unpack tarball, reason: %s\n", err)
	}
	log.Debugf("Unpacked install.tar.xz to temp dir '%s'\n", temp)
	name := filepath.Join(temp, "install.tar")
	tarFile, err := os.Open(name)
	if err != nil {
		log.Fatalf("Failed to open tar '%s', reason: %s\n", name, err)
	}
	log.Debugf("Opened tar '%s'\n", name)
	files := tar.NewReader(tarFile)
	h, err := files.Next()
	for err == nil {
		if h.Size == 0 {
			h, err = files.Next()
			continue
		}
		if h.Typeflag == tar.TypeDir {
			h, err = files.Next()
			continue
		}
		// ignore statically linked archives, debug symbols and Guile 3.x JIT .go files compiled to native ELF-format
		if strings.HasSuffix(h.Name, ".o") ||strings.HasSuffix(h.Name, ".la") || strings.HasSuffix(h.Name, ".a") || strings.HasSuffix(h.Name, ".debug") || strings.HasSuffix(h.Name, ".debuginfo") || strings.HasSuffix(h.Name, ".go") {
			h, err = files.Next()
			continue
		}
		var raw []byte
		if raw, err = ioutil.ReadAll(files); err != nil {
			tarFile.Close()
			log.Fatalf("Failed to read file '%s', reason: %s\n", h.Name, err)
		}
		if err = r.AddFile(bytes.NewReader(raw), filepath.Base(h.Name)); err != nil && err != io.EOF {
			tarFile.Close()
			log.Fatalf("Failed to add file '%s', reason: %s\n", h.Name, err)
		}
		log.Debugf("Processed tar entry '%s'\n", h.Name)
		h, err = files.Next()
	}
	if err != nil && err != io.EOF {
		tarFile.Close()
		log.Fatalf("Failed to read from tar '%s', reason: %s\n", name, err)
	}
	tarFile.Close()
	log.Goodln("Done")
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: yabi [eopkgs...]")
		os.Exit(1)
	}
	log.SetFormat(format.Min)
	log.SetLevel(level.Info)
	r := make(abi.Report)
	for _, eopkg := range os.Args[1:] {
		AddPackage(r, eopkg)
	}
	missing, err := r.Resolve()
	if err != nil {
		log.Fatalf("Failed to resolve symbols, reason: %s\n", err)
	}
    if len(missing) > 0 {
	    log.Errorln("Failed to find libraries:")
    	for _, lib := range missing {
	    	log.Errorln("\t" + lib)
	    }
    }
	if err := r.Save("."); err != nil {
		log.Fatalf("Failed to save ABI reports, reason: %s\n", err)
	}
}
