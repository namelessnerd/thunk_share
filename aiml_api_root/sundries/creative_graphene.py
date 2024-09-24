import graphene
from .types import CreativesForCampaignType
from ..models import AdCreative, Campaign
from lib.core.aiml.creatives import generate_creatives as gc

class TrackerQuery(graphene.ObjectType):
    creatives_for_campaign = graphene.Field(CreativesForCampaignType,
                                            nct_id=graphene.String(required=True),
                                            campaign_id=graphene.Int(required=True))

    def resolve_creatives_for_campaign(self, info, nct_id, campaign_id):
        
        # Check if creatives exist in the database for the campaign
        creatives = AdCreative.objects.filter(campaign__id=campaign_id)
        campaign = None
        try:
            campaign = Campaign.objects.get(pk=campaign_id)
        except ObjectDoesNotExist:
            raise Exception(f"Campaign with id {campaign_id} does not exist.")
        if not creatives.exists():
            # creatives do not exist. call the AI and generate creatives
            creatives = gc.generate(nct_id)
            # Iterate over each creative in the AI response and create an AdCreative object
            for creative_data in creatives:
                ad_creative = AdCreative(
                    campaign=campaign,
                    ai_source=creative_data.get('source'),
                    target_demo=creative_data.get('target_demo'),  # Ensure target_demo is stored as a list
                    headline=creative_data.get('headline'),
                    primary_text=creative_data.get('primary_text'),
                    description=creative_data.get('description'),
                    call_to_action=creative_data.get('call_to_action'),
                )
                ad_creative.save()  # Save to the database
        creatives = AdCreative.objects.filter(campaign__id=campaign_id)
        # Add campaign_name to each creative response
         return ({
            "campaign_name" : campaign.name,
            "creatives" : creatives
        })

        

