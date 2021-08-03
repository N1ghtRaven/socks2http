package config

import (
	"os"

	"golang.org/x/net/proxy"
)

type SocksProxyConfig struct {
	Address string
	Auth    proxy.Auth
}

type Config struct {
	SocksProxy SocksProxyConfig
}

func New() *Config {
	return &Config{
		SocksProxy: SocksProxyConfig{
			Address: getEnv("SOCKS_HOST", "127.0.0.1") + ":" + getEnv("SOCKS_PORT", "1080"),
			Auth: proxy.Auth{
				User:     getEnv("SOCKS_USERNAME", ""),
				Password: getEnv("SOCKS_PASSWORD", ""),
			},
		},
	}
}

func getEnv(key string, defaultVal string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}

	return defaultVal
}
