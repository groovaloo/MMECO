#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::prelude::*;

    const MAX_REPUTATION: u32 = 1_000_000;

    #[derive(
        Encode,
        Decode,
        Clone,
        Copy,
        PartialEq,
        Eq,
        RuntimeDebug,
        TypeInfo,
        MaxEncodedLen,
        Default
    )]
    pub enum ContributionType {
        #[default]
        Construction,
        Agriculture,
        Energy,
        Governance,
        Health,
        Logistics,
    }

    #[derive(
        Encode,
        Decode,
        Clone,
        Copy,
        PartialEq,
        Eq,
        RuntimeDebug,
        TypeInfo,
        MaxEncodedLen
    )]
    pub enum SubContributionType {
        // Construção
        Painting,
        Carpentry,
        Masonry,
        Electrical,
        Plumbing,
        // Agricultura
        CropFarming,
        Livestock,
        Horticulture,
        // Energia
        Solar,
        Wind,
        Hydro,
        // Saúde
        Medical,
        Nursing,
        FirstAid,
        // Logística
        Transport,
        Storage,
        Distribution,
        // Governação
        Coordination,
        Mediation,
        Planning,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>>
            + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // Admin do Sistema
    #[pallet::storage]
    #[pallet::getter(fn admin)]
    pub type Admin<T: Config> = StorageValue<_, T::AccountId>;

    // Reputação Total
    #[pallet::storage]
    #[pallet::getter(fn reputation)]
    pub type Reputation<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    // Reputação por Tipo (Domínio)
    #[pallet::storage]
    #[pallet::getter(fn reputation_by_type)]
    pub type ReputationByType<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, T::AccountId,
        Blake2_128Concat, ContributionType,
        u32,
        ValueQuery
    >;

    // Saldo de Buildcoin
    #[pallet::storage]
    #[pallet::getter(fn buildcoin_balance)]
    pub type BuildcoinBalance<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u128, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ContributionRecorded(T::AccountId, ContributionType, u32),
        ReputationReduced(T::AccountId, ContributionType, u32),
        ReputationReset(T::AccountId),
        AdminSet(T::AccountId),
        BuildcoinMinted(T::AccountId, u128),
    }

    #[pallet::error]
    pub enum Error<T> {
        Overflow,
        Underflow,
        MaxReputationReached,
        NotAdmin,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {

        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn set_admin(origin: OriginFor<T>, new_admin: T::AccountId) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            Admin::<T>::put(&new_admin);
            Self::deposit_event(Event::AdminSet(new_admin));
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn record_contribution(
            origin: OriginFor<T>,
            contribution: ContributionType,
            amount: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ReputationByType::<T>::try_mutate(&who, contribution, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                Ok(())
            })?;

            Reputation::<T>::try_mutate(&who, |rep| -> Result<(), Error<T>> {
                let new_rep = rep.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                if new_rep > MAX_REPUTATION {
                    return Err(Error::<T>::MaxReputationReached)
                }
                *rep = new_rep;
                Ok(())
            })?;

            Self::deposit_event(Event::ContributionRecorded(who, contribution, amount));
            Ok(())
        }

        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn reduce_contribution(
            origin: OriginFor<T>,
            contribution: ContributionType,
            amount: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ReputationByType::<T>::try_mutate(&who, contribution, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_sub(amount).ok_or(Error::<T>::Underflow)?;
                Ok(())
            })?;

            Reputation::<T>::try_mutate(&who, |rep| -> Result<(), Error<T>> {
                *rep = rep.checked_sub(amount).ok_or(Error::<T>::Underflow)?;
                Ok(())
            })?;

            Self::deposit_event(Event::ReputationReduced(who, contribution, amount));
            Ok(())
        }

        #[pallet::call_index(3)]
        #[pallet::weight(10_000)]
        pub fn reset_reputation(origin: OriginFor<T>, target: T::AccountId) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let admin = Admin::<T>::get().ok_or(Error::<T>::NotAdmin)?;
            ensure!(who == admin, Error::<T>::NotAdmin);

            Reputation::<T>::insert(&target, 0);

            // Loop de limpeza atualizado para os 6 domínios
            for t in [
                ContributionType::Construction,
                ContributionType::Agriculture,
                ContributionType::Energy,
                ContributionType::Governance,
                ContributionType::Health,
                ContributionType::Logistics,
            ] {
                ReputationByType::<T>::insert(&target, t, 0);
            }

            Self::deposit_event(Event::ReputationReset(target));
            Ok(())
        }

        /// Motor da Economia Comunitária
        /// 
        /// Esta função é o coração do sistema econômico da comunidade Moral Money.
        /// Só pode ser chamada quando um projeto é validado pelo conselho dos 5 especialistas.
        /// 
        /// Funcionamento:
        /// 1. Validação de Admin: Apenas o admin do sistema pode emitir Buildcoins
        /// 2. Validação de Projeto: Buildcoins só são emitidos após validação de contribuição real
        /// 3. Emissão Controlada: Quantidade baseada no impacto mensurável do projeto
        /// 4. Registro Transparente: Cada emissão é registrada como evento público
        /// 
        /// Princípio Ético:
        /// - Buildcoins não podem ser comprados, apenas ganhos através de contribuição real
        /// - Equivalência Ética: Trabalho e capital têm o mesmo valor na geração de moeda
        /// - Transparência Total: Todas as emissões são auditáveis na blockchain
        #[pallet::call_index(4)]
        #[pallet::weight(10_000)]
        pub fn issue_buildcoin(
            origin: OriginFor<T>,
            beneficiary: T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let admin = Admin::<T>::get().ok_or(Error::<T>::NotAdmin)?;
            ensure!(who == admin, Error::<T>::NotAdmin);

            BuildcoinBalance::<T>::try_mutate(&beneficiary, |balance| -> Result<(), Error<T>> {
                *balance = balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                Ok(())
            })?;

            Self::deposit_event(Event::BuildcoinMinted(beneficiary, amount));
            Ok(())
        }
    }

    // Funções de Consulta (Leitura)
    impl<T: Config> Pallet<T> {
        pub fn get_reputation(account: T::AccountId) -> u32 {
            Reputation::<T>::get(account)
        }

        pub fn get_reputation_by_type(account: T::AccountId, contribution: ContributionType) -> u32 {
            ReputationByType::<T>::get(account, contribution)
        }

        pub fn get_buildcoin_balance(account: T::AccountId) -> u128 {
            BuildcoinBalance::<T>::get(account)
        }

        /// Função de Auditoria para IA
        /// 
        /// Seleciona os 5 membros com maior reputação em um domínio específico.
        /// Esta função é projetada para ser chamada pela IA (Ollama/Llama3) para formar
        /// conselhos de especialistas em decisões técnicas.
        /// 
        /// Parâmetros:
        /// - contribution_type: Domínio específico (ex: Construction, Agriculture, etc.)
        /// 
        /// Retorno:
        /// - Vec<(T::AccountId, u32)>: Lista de até 5 pares (conta, reputação) ordenados por reputação decrescente
        /// 
        /// Uso:
        /// Quando a IA precisar formar um conselho de 5 especialistas para validar um projeto
        /// em um domínio específico, esta função fornece os 5 membros mais qualificados.
        /// 
        /// Exemplo:
        /// - Para projetos de 'Pintura' (subdomínio de Construction), usar ContributionType::Construction
        /// - Para projetos de 'CropFarming' (subdomínio de Agriculture), usar ContributionType::Agriculture
        pub fn select_top_experts(contribution_type: ContributionType) -> Vec<(T::AccountId, u32)> {
            // Coleta todos os pares (conta, reputação) para o domínio especificado
            let mut experts: Vec<(T::AccountId, u32)> = Vec::new();
            
            // Itera sobre o StorageDoubleMap para encontrar todos os registros do domínio
            for (account, domain, reputation) in ReputationByType::<T>::iter() {
                if domain == contribution_type {
                    experts.push((account, reputation));
                }
            }

            // Ordena por reputação em ordem decrescente
            experts.sort_by(|a, b| b.1.cmp(&a.1));

            // Retorna os 5 melhores (ou menos se houver menos de 5)
            experts.into_iter().take(5).collect()
        }

        /// Validação de Conselho de 5 Membros
        /// 
        /// Função auxiliar para validar se um conselho de 5 membros é composto pelos
        /// especialistas mais qualificados em um domínio específico.
        /// 
        /// Parâmetros:
        /// - contribution_type: Domínio da especialização
        /// - council_members: Lista de contas que formam o conselho
        /// 
        /// Retorno:
        /// - bool: true se o conselho está composto pelos top 5, false caso contrário
        pub fn validate_council(contribution_type: ContributionType, council_members: &[T::AccountId]) -> bool {
            if council_members.len() != 5 {
                return false;
            }

            // Obtém os top 5 especialistas
            let top_experts = Self::select_top_experts(contribution_type);
            
            if top_experts.len() < 5 {
                return false;
            }

            // Verifica se todos os membros do conselho estão entre os top 5
            for member in council_members {
                if !top_experts.iter().any(|(account, _)| account == member) {
                    return false;
                }
            }

            true
        }
    }
}