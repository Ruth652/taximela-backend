from domain.contribution_model import Contribute

class submitContributionsUsecase:
    def __init__(self, contribution_repo):
        self.contribution_repo = contribution_repo
        
    
    
    async def execute(self, data):
        contribution = Contribute(
            user_id=data.user_id,
            target_type=data.target_type,
            description=data.description,
            trust_score_at_submit=data.trust_score_at_submit,
        )
        return await self.contribution_repo.save(contribution)
