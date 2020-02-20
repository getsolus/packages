/*
 * Copyright 2018 Solus Project <copyright@getsol.us>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"os/user"
	"sort"
)

const defaultHost = "https://dev.getsol.us/api/"

var excludes = []string{
	"budgie-desktop-src",
	"budgie-desktop-branding-src",
	"gnome-desktop-branding-src",
	"infrastructure-tooling",
	"linux-next",
	"plasma-desktop-branding-src",
	"solus-appstream-data",
	"solus-image-budgie",
	"solus-image-gnome",
	"solus-image-i3",
	"solus-image-mate",
	"solus-image-plasma",
	"solus-site",
	"solus-site-backend",
	"solus-site-styling",
	"solus-webplatform-js",
	"ypkg-next-gen",
}

type ARCRC struct {
	Hosts map[string]map[string]string `json:"hosts"`
}

type Repo struct {
	Fields struct {
		ShortName string `json:"shortName"`
	} `json:"fields"`
}

type RepoResult struct {
	Data   []Repo `json:"data"`
	Cursor struct {
		After string `json:"after"`
	} `json:"cursor"`
}

type RepoResults struct {
	Result RepoResult `json:"result"`
}

func main() {
	u, err := user.Current()
	if err != nil {
		panic(err.Error())
	}
	config, err := os.Open(u.HomeDir + "/.arcrc")
	if err != nil {
		panic(err.Error())
	}
	defer config.Close()
	dec := json.NewDecoder(config)
	var arcrc ARCRC
	err = dec.Decode(&arcrc)
	if err != nil {
		panic(err.Error())
	}
	hostConfig, ok := arcrc.Hosts[defaultHost]
	if !ok || len(hostConfig) == 0 {
		panic("No host config found.")
	}
	token, ok := hostConfig["token"]
	if !ok || len(token) == 0 {
		panic("No host token found.")
	}
	repos := make([]string, 0)
	var next string
	var resp *http.Response
	for {
		if len(next) > 0 {
			resp, err = http.PostForm(defaultHost+"diffusion.repository.search",
				url.Values{"api.token": {token}, "after": {next}, "queryKey": {"active"}})
		} else {
			resp, err = http.PostForm(defaultHost+"diffusion.repository.search",
				url.Values{"api.token": {token}, "queryKey": {"active"}})
		}
		if err != nil {
			panic(err.Error())
		}
		dec2 := json.NewDecoder(resp.Body)
		var results RepoResults
		err = dec2.Decode(&results)
		resp.Body.Close()
		if err != nil {
			panic(err.Error())
		}
		for _, repo := range results.Result.Data {
			excluded := false
			for _, e := range excludes {
				if e == repo.Fields.ShortName {
					excluded = true
					break
				}
			}
			if excluded {
				continue
			}
			repos = append(repos, repo.Fields.ShortName)
		}
		next = results.Result.Cursor.After
		if len(next) == 0 {
			break
		}
	}
	sort.Strings(repos)
	for _, repo := range repos {
		fmt.Println(repo)
	}
}
