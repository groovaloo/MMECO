impl_runtime_apis! {
    impl polkadot_sdk::sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion { VERSION }
        fn execute_block(block: Block) { Executive::execute_block(block); }
        fn initialize_block(header: &<Block as BlockT>::Header) -> polkadot_sdk::sp_runtime::ExtrinsicInclusionMode {
            Executive::initialize_block(header)
        }
    }

    impl polkadot_sdk::sp_api::Metadata<Block> for Runtime {
        fn metadata() -> polkadot_sdk::sp_core::OpaqueMetadata {
            polkadot_sdk::sp_core::OpaqueMetadata::new(Runtime::metadata().into())
        }
        fn metadata_at_version(version: u32) -> Option<polkadot_sdk::sp_core::OpaqueMetadata> {
            Runtime::metadata_at_version(version)
        }
        fn metadata_versions() -> polkadot_sdk::sp_std::vec::Vec<u32> {
            Runtime::metadata_versions()
        }
    }

    impl polkadot_sdk::sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> ApplyExtrinsicResult {
            Executive::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            Executive::finalize_block()
        }
        fn inherent_extrinsics(data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_std::vec::Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(block: Block, data: polkadot_sdk::sp_inherents::InherentData) -> polkadot_sdk::sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl polkadot_sdk::sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(
            source: TransactionSource,
            tx: <Block as BlockT>::Extrinsic,
            block_hash: <Block as BlockT>::Hash,
        ) -> TransactionValidity {
            Executive::validate_transaction(source, tx, block_hash)
        }
    }

    impl polkadot_sdk::sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            Executive::offchain_worker(header)
        }
    }

    impl polkadot_sdk::sp_genesis_builder::GenesisBuilder<Block> for Runtime {
        fn build_state(config: polkadot_sdk::sp_std::vec::Vec<u8>) -> polkadot_sdk::sp_genesis_builder::Result {
            build_state::<RuntimeGenesisConfig>(config)
        }
        fn get_preset(id: &Option<polkadot_sdk::sp_genesis_builder::PresetId>) -> Option<polkadot_sdk::sp_std::vec::Vec<u8>> {
            get_preset::<RuntimeGenesisConfig>(id, |_| None)
        }
        fn preset_names() -> polkadot_sdk::sp_std::vec::Vec<polkadot_sdk::sp_genesis_builder::PresetId> {
            polkadot_sdk::sp_std::vec![]
        }
    }
}
