package shared

import (
	"crypto"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// HashSource gets the Hash for a given source
func HashSource(URI string) (hash string, hashErr error) {
	var in io.ReadCloser

	if strings.HasPrefix(URI, "git|") {
		// Git sources
		pieces := strings.Split(URI, ":")
		if len(pieces) < 3 {
			hashErr = fmt.Errorf("no hash in git URI, should resemble 'git|http://path/to/repo:commit hash")
			return
		}

		hash = pieces[len(pieces)-1]
		return
	} else if strings.HasPrefix(URI, "file://") {
		// Local File sources
		in, hashErr = os.Open(strings.TrimPrefix(URI, "file://"))

		if hashErr != nil {
			return
		}

		defer in.Close()
	} else if strings.HasPrefix(URI, "http") {
		// HTTP Sources
		var r *http.Response
		r, hashErr = http.Get(URI)

		if hashErr != nil {
			return
		}

		in = r.Body
		defer r.Body.Close()
	} else {
		hashErr = fmt.Errorf("unsupported source type")
		return
	}

	// All hashed are SHA256 hashes
	shaHash := crypto.SHA256.New()
	_, hashErr = io.Copy(shaHash, in)

	if hashErr != nil {
		return
	}

	hash = fmt.Sprintf("%x", shaHash.Sum(nil))
	return
}

// UpdateSources gets the hashes for one or more URI sources
func UpdateSources(URIs []string) ([]map[string]string, error) {
	srcs := make([]map[string]string, 0)
	// for each URI
	for _, URI := range URIs {
		// - URI : HASH
		src := make(map[string]string)
		// Get Hash for URI
		h, err := HashSource(URI)
		if err != nil {
			return srcs, err
		}
		src[URI] = h
		// Add source to all sources
		srcs = append(srcs, src)
	}
	return srcs, nil
}
