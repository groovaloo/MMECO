.PHONY: init build run clean

# Prepara o ambiente para Polkadot SDK 2025
init:
	rustup target add wasm32-unknown-unknown
	rustup component add rust-src

# Compila o nó Moral Money
build:
	cargo build --release

# Limpa e arranca o nó em modo dev
run:
	./target/release/mmeco-node purge-chain --dev -y
	./target/release/mmeco-node --dev

# Limpa a lixeira de compilações antigas
clean:
	cargo clean
