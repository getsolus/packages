/*
 * Copyright 2020 Solus Project <copyright@getsol.us>
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
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"os/user"
)

const defaultHost = "https://dev.getsol.us/api/"

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
	repos := make(map[string]bool)
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
			repos[repo.Fields.ShortName] = true
		}
		next = results.Result.Cursor.After
		if len(next) == 0 {
			break
		}
	}
	dirs, err := ioutil.ReadDir(".")
	if err != nil {
		panic(err.Error())
	}
	stdin := bufio.NewReader(os.Stdin)
	remove := false
	done := false
	for !done {
		fmt.Println("Would you like to remove of all non-active repos? (yes/no)")
		ans, err := stdin.ReadString('\n')
		if err != nil {
			panic(err.Error())
		}
		switch ans {
		case "yes\n":
			remove = true
			done = true
		case "no\n":
			remove = false
			done = true
		default:
			fmt.Printf("'%s' is not a valid answer", ans)
		}
	}
	for _, dir := range dirs {
		if !dir.IsDir() {
			continue
		}
		if !repos[dir.Name()] {
			fmt.Printf("Repository '%s' is not active\n", dir.Name())
			if remove {
				fmt.Printf("Removing repository '%s'...", dir.Name())
				if err := os.RemoveAll("./" + dir.Name()); err != nil {
					fmt.Printf("FAILED: %s\n", err.Error())
				} else {
					fmt.Println("DONE")
				}
			}
		}
	}
}
