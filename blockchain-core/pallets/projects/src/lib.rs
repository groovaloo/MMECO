#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    // Import types from reputation pallet
    pub use pallet_reputation::pallet::{ContributionType, SubContributionType};

    pub const MAX_NAME_LEN: u32 = 100;
    pub const MAX_DESC_LEN: u32 = 500;
    pub const MAX_PARTICIPANTS: u32 = 256;
    pub const MAX_PROJECTS_PER_STATUS: u32 = 10_000;

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
    pub enum ProjectStatus {
        Created,
        Active,
        Completed,
        Evaluated,
        Cancelled,
    }

    #[derive(
        Encode,
        Decode,
        Clone,
        PartialEq,
        Eq,
        RuntimeDebug,
        TypeInfo,
        MaxEncodedLen
    )]
    pub struct Project<AccountId: MaxEncodedLen> {
        pub id: u64,
        pub creator: AccountId,
        pub name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
        pub description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
        pub domain: ContributionType,
        pub sub_domain: SubContributionType,
        pub status: ProjectStatus,
        pub participants: BoundedVec<AccountId, ConstU32<MAX_PARTICIPANTS>>,
        pub created_at: u64,
        pub completed_at: Option<u64>,
        pub impact_score: Option<u32>,
    }

    #[derive(
        Encode,
        Decode,
        Clone,
        PartialEq,
        Eq,
        RuntimeDebug,
        TypeInfo,
        MaxEncodedLen
    )]
    pub struct ProjectParticipant<AccountId> {
        pub project_id: u64,
        pub participant: AccountId,
        pub joined_at: u64,
        pub contribution_amount: u32,
        pub validated: bool,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>>
            + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        // Link to reputation pallet for updating reputation
        type Reputation: frame_system::Config + pallet_reputation::Config;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // Storage for projects
    #[pallet::storage]
    #[pallet::getter(fn project)]
    pub type Projects<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64,
        Project<T::AccountId>,
        OptionQuery
    >;

    // Storage for project participants
    #[pallet::storage]
    #[pallet::getter(fn project_participant)]
    pub type ProjectParticipants<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, u64,
        Blake2_128Concat, T::AccountId,
        ProjectParticipant<T::AccountId>,
        OptionQuery
    >;

    // Counter for project IDs
    #[pallet::storage]
    #[pallet::getter(fn project_counter)]
    pub type ProjectCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    // Projects by status for querying
    #[pallet::storage]
    #[pallet::getter(fn projects_by_status)]
    pub type ProjectsByStatus<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ProjectStatus,
        BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>>,
        ValueQuery
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ProjectCreated(T::AccountId, u64, ContributionType),
        ProjectJoined(T::AccountId, u64),
        ProjectCompleted(T::AccountId, u64),
        ProjectEvaluated(u64, u32),
        ProjectCancelled(T::AccountId, u64),
    }

    #[pallet::error]
    pub enum Error<T> {
        ProjectNotFound,
        ProjectAlreadyCompleted,
        ProjectNotActive,
        ProjectNotCompleted,
        AlreadyParticipant,
        NotParticipant,
        NotProjectCreator,
        MaxProjectNameLengthExceeded,
        MaxProjectDescriptionLengthExceeded,
        InvalidImpactScore,
        Overflow,
        TooManyParticipants,
        TooManyProjects,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {

        /// Create a new project
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn create_project(
            origin: OriginFor<T>,
            name: BoundedVec<u8, ConstU32<MAX_NAME_LEN>>,
            description: BoundedVec<u8, ConstU32<MAX_DESC_LEN>>,
            domain: ContributionType,
            sub_domain: SubContributionType,
        ) -> DispatchResult {
            let creator = ensure_signed(origin)?;

            let project_id = Self::project_counter();
            let block = <frame_system::Pallet<T>>::block_number();
            let created_at: u64 = block.try_into().unwrap_or(0u64);

            let mut participants: BoundedVec<T::AccountId, ConstU32<MAX_PARTICIPANTS>> =
                BoundedVec::default();
            participants.try_push(creator.clone()).map_err(|_| Error::<T>::TooManyParticipants)?;

            let project = Project {
                id: project_id,
                creator: creator.clone(),
                name,
                description,
                domain,
                sub_domain,
                status: ProjectStatus::Created,
                participants,
                created_at,
                completed_at: None,
                impact_score: None,
            };

            Projects::<T>::insert(project_id, &project);

            let participant = ProjectParticipant {
                project_id,
                participant: creator.clone(),
                joined_at: created_at,
                contribution_amount: 0,
                validated: false,
            };
            ProjectParticipants::<T>::insert(project_id, &creator, participant);

            ProjectCounter::<T>::set(project_id + 1);

            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Created, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCreated(creator, project_id, domain));
            Ok(())
        }

        /// Join an existing project
        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn join_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let participant = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(
                project.status == ProjectStatus::Created || project.status == ProjectStatus::Active,
                Error::<T>::ProjectNotActive
            );

            ensure!(
                Self::project_participant(project_id, &participant).is_none(),
                Error::<T>::AlreadyParticipant
            );

            let block = <frame_system::Pallet<T>>::block_number();
            let joined_at: u64 = block.try_into().unwrap_or(0u64);

            let participant_record = ProjectParticipant {
                project_id,
                participant: participant.clone(),
                joined_at,
                contribution_amount: 0,
                validated: false,
            };
            ProjectParticipants::<T>::insert(project_id, &participant, participant_record);

            if project.status == ProjectStatus::Created {
                project.status = ProjectStatus::Active;
                Projects::<T>::insert(project_id, &project);

                ProjectsByStatus::<T>::mutate(ProjectStatus::Created, |v| {
                    v.retain(|&id| id != project_id);
                });
                ProjectsByStatus::<T>::try_mutate(ProjectStatus::Active, |v| {
                    v.try_push(project_id)
                }).map_err(|_| Error::<T>::TooManyProjects)?;
            }

            Self::deposit_event(Event::ProjectJoined(participant, project_id));
            Ok(())
        }

        /// Complete a project (only creator can do this)
        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn complete_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.creator == who, Error::<T>::NotProjectCreator);
            ensure!(project.status == ProjectStatus::Active, Error::<T>::ProjectNotActive);

            let block = <frame_system::Pallet<T>>::block_number();
            let completed_at: u64 = block.try_into().unwrap_or(0u64);

            project.status = ProjectStatus::Completed;
            project.completed_at = Some(completed_at);
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Active, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Completed, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCompleted(who, project_id));
            Ok(())
        }

        /// Evaluate a completed project and set impact score
        #[pallet::call_index(3)]
        #[pallet::weight(10_000)]
        pub fn evaluate_project(
            origin: OriginFor<T>,
            project_id: u64,
            impact_score: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.status == ProjectStatus::Completed, Error::<T>::ProjectNotCompleted);
            ensure!(impact_score > 0 && impact_score <= 1000, Error::<T>::InvalidImpactScore);

            project.status = ProjectStatus::Evaluated;
            project.impact_score = Some(impact_score);
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Completed, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Evaluated, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectEvaluated(project_id, impact_score));
            Ok(())
        }

        /// Cancel a project (only creator can do this)
        #[pallet::call_index(4)]
        #[pallet::weight(10_000)]
        pub fn cancel_project(
            origin: OriginFor<T>,
            project_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.creator == who, Error::<T>::NotProjectCreator);
            ensure!(
                project.status == ProjectStatus::Created || project.status == ProjectStatus::Active,
                Error::<T>::ProjectNotActive
            );

            project.status = ProjectStatus::Cancelled;
            Projects::<T>::insert(project_id, &project);

            ProjectsByStatus::<T>::mutate(ProjectStatus::Created, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::mutate(ProjectStatus::Active, |v| {
                v.retain(|&id| id != project_id);
            });
            ProjectsByStatus::<T>::try_mutate(ProjectStatus::Cancelled, |v| {
                v.try_push(project_id)
            }).map_err(|_| Error::<T>::TooManyProjects)?;

            Self::deposit_event(Event::ProjectCancelled(who, project_id));
            Ok(())
        }

        /// Record contribution for a participant
        #[pallet::call_index(5)]
        #[pallet::weight(10_000)]
        pub fn record_contribution(
            origin: OriginFor<T>,
            project_id: u64,
            contribution_amount: u32,
        ) -> DispatchResult {
            let participant = ensure_signed(origin)?;

            let project = Self::project(project_id).ok_or(Error::<T>::ProjectNotFound)?;
            ensure!(project.status == ProjectStatus::Active, Error::<T>::ProjectNotActive);

            let mut participant_record = Self::project_participant(project_id, &participant)
                .ok_or(Error::<T>::NotParticipant)?;

            participant_record.contribution_amount = participant_record.contribution_amount
                .checked_add(contribution_amount)
                .ok_or(Error::<T>::Overflow)?;

            ProjectParticipants::<T>::insert(project_id, &participant, participant_record);

            Ok(())
        }
    }

    // Helper functions for external access
    impl<T: Config> Pallet<T> {
        /// Get all projects by status
        pub fn get_projects_by_status(status: ProjectStatus) -> BoundedVec<u64, ConstU32<MAX_PROJECTS_PER_STATUS>> {
            Self::projects_by_status(status)
        }

        /// Get project details
        pub fn get_project(project_id: u64) -> Option<Project<T::AccountId>> {
            Self::project(project_id)
        }

        /// Get all participants of a project
        pub fn get_project_participants(project_id: u64) -> sp_std::vec::Vec<T::AccountId> {
            let mut participants = sp_std::vec::Vec::new();
            for (pid, participant, _) in ProjectParticipants::<T>::iter() {
                if pid == project_id {
                    participants.push(participant);
                }
            }
            participants
        }

        /// Get participant details for a specific project
        pub fn get_participant(
            project_id: u64,
            account: &T::AccountId,
        ) -> Option<ProjectParticipant<T::AccountId>> {
            Self::project_participant(project_id, account)
        }
    }
}
