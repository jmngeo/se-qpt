"""
SE Training Strategy Selection Engine
Implements the decision logic for recommending appropriate training strategies
based on maturity assessment and target group size.
"""

# 7 SE Training Strategies Data Structure
SE_TRAINING_STRATEGIES = [
    {
        'id': 'se_for_managers',
        'name': 'SE for Managers',
        'category': 'FOUNDATIONAL',
        'description': 'This strategy focuses in particular on managers. They play a major role in the introduction of SE, particularly with regard to change management. They are enablers of change in a company and therefore need an understanding of what it means to introduce and use SE.',
        'qualificationLevel': 'Understanding',
        'suitablePhase': 'Introductory Phase',
        'targetAudience': 'Management and Leadership',
        'groupSize': {
            'min': 5,
            'max': 30,
            'optimal': '10-20 managers'
        },
        'duration': '1-2 days workshop',
        'benefits': [
            'Creates top-level buy-in',
            'Enables change management',
            'Communicates SE benefits clearly'
        ],
        'implementation': {
            'format': 'Executive Workshop',
            'frequency': 'One-time or quarterly refresh',
            'prerequisites': 'None'
        }
    },

    {
        'id': 'common_understanding',
        'name': 'Common Basic Understanding',
        'category': 'AWARENESS',
        'description': 'This strategy is an approach that focuses on interdisciplinary exchange and thus creates awareness for the topic of SE. The focus here is on understanding the fundamental interrelationships of SE as part of basic training and reflecting on them in the group.',
        'qualificationLevel': 'Recognition',
        'suitablePhase': 'Motivation Phase',
        'targetAudience': 'All stakeholders regardless of expertise',
        'groupSize': {
            'min': 10,
            'max': 100,
            'optimal': '20-50 participants'
        },
        'duration': '2-3 days',
        'benefits': [
            'Standardized vocabulary',
            'Low barrier to entry',
            'Breaking down silo thinking',
            'Broad participation possible'
        ],
        'drawbacks': [
            'No project reference',
            'Little depth of content',
            'Less acceptance without practical context'
        ]
    },

    {
        'id': 'orientation_pilot',
        'name': 'Orientation in Pilot Project',
        'category': 'APPLICATION',
        'description': 'The strategy follows an application-oriented approach to qualification. Participants should gain an orientation in SE while applying SE in a pilot project. A team of developers is trained and recognizes the added value of SE through its application.',
        'qualificationLevel': 'Application',
        'suitablePhase': 'Initial Implementation',
        'targetAudience': 'Development teams',
        'groupSize': {
            'min': 5,
            'max': 20,
            'optimal': '8-15 team members'
        },
        'duration': 'Initial intro + continuous coaching (3-6 months)',
        'benefits': [
            'High acceptance',
            'Measurable benefit',
            'Direct testing of content',
            'Motivation through visible success'
        ],
        'drawbacks': [
            'Effectiveness depends on project',
            'Not useful for all roles',
            'Time pressure on project makes learning difficult',
            'Suitable project necessary'
        ]
    },

    {
        'id': 'certification',
        'name': 'Certification',
        'category': 'SPECIALIZATION',
        'description': 'Certifications provide fixed and standardized training content with certification certificates. Typical certifications for SE are SE-Zert and CSEP. Suitable for creating internal SE experts.',
        'qualificationLevel': 'Application',
        'suitablePhase': 'Motivation Phase',
        'targetAudience': 'SE specialists and experts',
        'groupSize': {
            'min': 1,
            'max': 25,
            'optimal': '5-15 specialists'
        },
        'duration': '5-10 days intensive',
        'certificationOptions': ['SE-Zert', 'CSEP', 'INCOSE'],
        'benefits': [
            'High standard',
            'International recognition',
            'Technical depth',
            'Ideal for specialists'
        ],
        'drawbacks': [
            'No project reference',
            'Low transferability without company-wide introduction',
            'Cost-intensive'
        ]
    },

    {
        'id': 'continuous_support',
        'name': 'Continuous Support',
        'category': 'SUSTAINMENT',
        'description': 'This qualification strategy focuses on continuous learning in an organization. Based on self-directed, proactive learning, employee queries are collected, documented and answered.',
        'qualificationLevel': 'Application',
        'suitablePhase': 'Continuation Phase',
        'targetAudience': 'All employees in SE environment',
        'groupSize': {
            'min': 20,
            'max': 'Unlimited',
            'optimal': 'Scalable to entire organization'
        },
        'duration': 'Ongoing',
        'requirements': [
            'Trained organization',
            'Defined processes, methods, and tools',
            'Established SE culture'
        ],
        'benefits': [
            'Continuous improvement',
            'Just-in-time learning',
            'Cost-effective at scale',
            'Maintains SE momentum'
        ]
    },

    {
        'id': 'needs_based_project',
        'name': 'Needs-based Project-oriented Training',
        'category': 'TARGETED',
        'description': 'This strategy is aimed at targeted further training for specific roles within the company. Projects are accompanied over a longer period with basic and expert knowledge imparted through training courses.',
        'qualificationLevel': 'Understanding to Application',
        'suitablePhase': 'Implementation Phase',
        'targetAudience': 'Specific roles in projects',
        'groupSize': {
            'min': 10,
            'max': 50,
            'optimal': '15-30 per cohort'
        },
        'duration': 'Project lifecycle (6-12 months)',
        'structure': [
            'Basic training for all participants',
            'Role-specific deepening',
            'Repeated topic-specific sessions'
        ],
        'requirements': [
            'Defined processes, methods, and tools',
            'Specified roles and tasks'
        ],
        'benefits': [
            'Role-specific content',
            'Direct application',
            'Progressive skill building'
        ]
    },

    {
        'id': 'train_the_trainer',
        'name': 'Train the SE-Trainer',
        'category': 'MULTIPLIER',
        'description': 'This strategy focuses on training coaches and trainers with the task of bringing SE into the company. Covers company challenges, SE skills, and didactic/moderation skills.',
        'qualificationLevel': 'Mastery',
        'suitablePhase': 'All phases (supplementary)',
        'targetAudience': 'Internal trainers or external providers',
        'groupSize': {
            'min': 2,
            'max': 10,
            'optimal': '4-6 trainers'
        },
        'duration': '10-20 days intensive + practice',
        'trainingAreas': [
            'Company challenges and working methods',
            'Necessary SE skills',
            'Didactic and moderation skills'
        ],
        'decisionFactors': {
            'internal': {
                'pros': ['Repeated training without additional costs', 'Deep company knowledge'],
                'cons': ['Extensive upfront training required', 'Time investment']
            },
            'external': {
                'pros': ['Existing SE knowledge', 'Quick deployment'],
                'cons': ['Needs company adaptation', 'Ongoing costs']
            }
        }
    }
]


class StrategySelectionEngine:
    """
    Decision engine for SE training strategy selection
    Based on maturity assessment and target group size
    """

    def __init__(self, maturity_data, target_group_data):
        """
        Initialize the engine with maturity and target group data

        Args:
            maturity_data: dict with keys: rollout_scope, se_processes, se_mindset, knowledge_base, final_score, maturity_level
            target_group_data: dict with keys: size_range, size_category, estimated_count
        """
        self.maturity_data = maturity_data
        self.target_group_data = target_group_data
        self.selected_strategies = []
        self.decision_path = []

    def select_strategies(self):
        """
        Main method to select appropriate strategies
        Returns dict with strategies, decision_path, and reasoning
        """
        # Step 1: Evaluate Train-the-Trainer need
        self.evaluate_train_the_trainer()

        # Step 2: Main strategy selection based on maturity
        se_processes_value = self.maturity_data.get('se_processes', 0)
        rollout_scope_value = self.maturity_data.get('rollout_scope', 0)

        if se_processes_value <= 2:
            # Low maturity path: Motivation Phase (levels 0-2: Not Available, Ad hoc, Individually Controlled)
            self.select_low_maturity_strategies()
        else:
            # Higher maturity path: Implementation/Continuation Phase (levels 3+: Defined and Established onwards)
            self.select_high_maturity_strategies(rollout_scope_value)

        # Step 3: Validate strategies against target group size
        self.validate_against_group_size()

        return {
            'strategies': self.selected_strategies,
            'decisionPath': self.decision_path,
            'reasoning': self.generate_reasoning(),
            'requiresUserChoice': self.requires_secondary_selection()
        }

    def evaluate_train_the_trainer(self):
        """Determine if Train-the-Trainer should be added"""
        estimated_count = self.target_group_data.get('estimated_count', 0)
        size_category = self.target_group_data.get('size_category', 'SMALL')

        # Add train-the-trainer for large organizations
        should_add_trainer = (
            estimated_count >= 100 or
            size_category in ['LARGE', 'VERY_LARGE', 'ENTERPRISE']
        )

        if should_add_trainer:
            self.selected_strategies.append({
                'strategy': 'train_the_trainer',
                'strategyName': 'Train the SE-Trainer',
                'priority': 'SUPPLEMENTARY',
                'reason': f"With {self.target_group_data.get('size_range', 'large')} people to train, a train-the-trainer approach will enable scalable knowledge transfer"
            })

            self.decision_path.append({
                'step': 1,
                'decision': 'Add Train-the-Trainer',
                'reason': 'Large target group requires multiplier approach'
            })

    def select_low_maturity_strategies(self):
        """Select strategies for organizations with low SE process maturity"""
        # Primary strategy for low maturity
        self.selected_strategies.append({
            'strategy': 'se_for_managers',
            'strategyName': 'SE for Managers',
            'priority': 'PRIMARY',
            'reason': 'Management buy-in is essential for SE introduction in organizations with undefined processes'
        })

        se_processes_value = self.maturity_data.get('se_processes', 0)

        self.decision_path.append({
            'step': 2,
            'decision': 'Select SE for Managers as primary',
            'reason': f"SE Processes maturity is \"{self.get_maturity_level_name(se_processes_value)}\" - requires management enablement first"
        })

        # For low maturity, user must choose a secondary strategy
        # This will be handled by the frontend (Pro-Con Comparison)
        self.decision_path.append({
            'step': 3,
            'decision': 'User selects secondary strategy',
            'options': ['common_understanding', 'orientation_pilot', 'certification']
        })

    def select_high_maturity_strategies(self, rollout_scope_value):
        """Select strategies for organizations with higher SE process maturity"""
        if rollout_scope_value <= 1:
            # Narrow rollout - needs expansion
            self.selected_strategies.append({
                'strategy': 'needs_based_project',
                'strategyName': 'Needs-based Project-oriented Training',
                'priority': 'PRIMARY',
                'reason': 'SE processes are defined but not widely deployed - needs targeted project-based training'
            })

            self.decision_path.append({
                'step': 2,
                'decision': 'Select Needs-based Project-oriented Training',
                'reason': f"Rollout scope is \"{self.get_rollout_level_name(rollout_scope_value)}\" - requires expansion through project training"
            })
        else:
            # Broad rollout - sustain and improve
            self.selected_strategies.append({
                'strategy': 'continuous_support',
                'strategyName': 'Continuous Support',
                'priority': 'PRIMARY',
                'reason': 'SE is widely deployed - requires continuous support for sustainment'
            })

            self.decision_path.append({
                'step': 2,
                'decision': 'Select Continuous Support',
                'reason': f"Rollout scope is \"{self.get_rollout_level_name(rollout_scope_value)}\" - focus on continuous improvement"
            })

    def requires_secondary_selection(self):
        """Check if user needs to select a secondary strategy"""
        se_processes_value = self.maturity_data.get('se_processes', 0)
        return se_processes_value <= 2

    def validate_against_group_size(self):
        """Check if selected strategies are appropriate for group size"""
        target_size = self.target_group_data.get('estimated_count', 0)

        for selection in self.selected_strategies:
            strategy = next((s for s in SE_TRAINING_STRATEGIES if s['id'] == selection['strategy']), None)
            if strategy:
                max_size = strategy['groupSize']['max']

                if max_size != 'Unlimited' and target_size > max_size:
                    selection['warning'] = f"Strategy typically supports up to {max_size} participants. Consider multiple cohorts or alternative approach."

    def generate_reasoning(self):
        """Generate detailed reasoning for the selection"""
        se_processes_value = self.maturity_data.get('se_processes', 0)
        rollout_scope_value = self.maturity_data.get('rollout_scope', 0)
        se_mindset_value = self.maturity_data.get('se_mindset', 0)
        knowledge_base_value = self.maturity_data.get('knowledge_base', 0)

        reasoning = {
            'maturityFactors': {
                'seProcesses': {
                    'value': se_processes_value,
                    'level': self.get_maturity_level_name(se_processes_value),
                    'implication': 'Organization needs foundational SE establishment and management enablement' if se_processes_value <= 2 else 'Organization has established SE processes ready for advanced training'
                },
                'rolloutScope': {
                    'value': rollout_scope_value,
                    'level': self.get_rollout_level_name(rollout_scope_value),
                    'implication': 'SE needs broader organizational deployment' if rollout_scope_value <= 1 else 'SE is already widely deployed'
                },
                'seMindset': {
                    'value': se_mindset_value,
                    'level': self.get_se_mindset_level_name(se_mindset_value),
                    'impact': 'Influences learning readiness and approach'
                },
                'knowledgeBase': {
                    'value': knowledge_base_value,
                    'level': self.get_knowledge_level_name(knowledge_base_value),
                    'impact': 'Affects available resources for training'
                }
            },
            'targetGroupConsiderations': {
                'size': self.target_group_data.get('size_range', 'Unknown'),
                'implication': self.get_group_size_implication()
            },
            'recommendations': self.generate_recommendations()
        }

        return reasoning

    def get_maturity_level_name(self, value):
        """Get human-readable name for SE processes maturity level"""
        levels = [
            'Not Available',
            'Ad hoc / Undefined',
            'Individually Controlled',
            'Defined and Established',
            'Quantitatively Predictable',
            'Optimized'
        ]
        return levels[value] if 0 <= value < len(levels) else 'Unknown'

    def get_rollout_level_name(self, value):
        """Get human-readable name for rollout scope level"""
        levels = [
            'Not Available',
            'Individual Area',
            'Development Area',
            'Company Wide',
            'Value Chain'
        ]
        return levels[value] if 0 <= value < len(levels) else 'Unknown'

    def get_se_mindset_level_name(self, value):
        """Get human-readable name for SE mindset level"""
        levels = [
            'Not Available',
            'Individual / Ad hoc',
            'Fragmented',
            'Established',
            'Optimized'
        ]
        return levels[value] if 0 <= value < len(levels) else 'Unknown'

    def get_knowledge_level_name(self, value):
        """Get human-readable name for knowledge base level"""
        levels = [
            'Not Available',
            'Individual / Ad hoc',
            'Fragmented',
            'Established',
            'Optimized'
        ]
        return levels[value] if 0 <= value < len(levels) else 'Unknown'

    def get_group_size_implication(self):
        """Get training implications based on group size"""
        size_category = self.target_group_data.get('size_category', 'SMALL')
        implications = {
            'SMALL': 'Suitable for intensive workshops and direct coaching',
            'MEDIUM': 'Requires mixed format approach with cohorts',
            'LARGE': 'Needs scalable formats and train-the-trainer approach',
            'VERY_LARGE': 'Requires phased rollout with multiple trainers',
            'ENTERPRISE': 'Demands enterprise learning program with LMS'
        }
        return implications.get(size_category, 'Group size considerations apply')

    def generate_recommendations(self):
        """Generate specific recommendations based on maturity profile"""
        recommendations = []

        se_processes_value = self.maturity_data.get('se_processes', 0)
        se_mindset_value = self.maturity_data.get('se_mindset', 0)
        knowledge_base_value = self.maturity_data.get('knowledge_base', 0)

        if se_processes_value <= 2:
            recommendations.append({
                'type': 'CRITICAL',
                'message': 'Focus on establishing management commitment and standardizing processes before broad rollout'
            })

        if se_mindset_value <= 1:
            recommendations.append({
                'type': 'IMPORTANT',
                'message': 'Emphasize cultural change and SE mindset development'
            })

        if knowledge_base_value <= 1:
            recommendations.append({
                'type': 'SUGGESTED',
                'message': 'Consider establishing knowledge management system alongside training'
            })

        return recommendations
