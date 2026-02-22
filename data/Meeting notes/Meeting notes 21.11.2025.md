Questions:



Q1. Strategy Selection Rules - Low Maturity

My Understanding: "If low maturity, the org selects 2 strategies - 'SE for managers' AND one of the 3 strategies (Common basic understanding, Orientation in pilot project, Certification)."



A. For low maturity pathway, if user selects 2 strategies with different target levels for the same competency, how do we handle it?

  - Example: "Common basic understanding" has Systems Thinking = Level 2

  - Example: "Certification" has Systems Thinking = Level 4

  - {Answered} **Do we take the HIGHER target (Level 4)**? - We pick the highest one. **But**, for *SE for managers*, we might need a separate section - in this half here, maybe we need to highlight the different levels or we might need to redefine LOs as they are now for Managers as well. Because Managers need to know more - what does it mean for my company level things? Instead of saying these are SE things, and this is how you apply it. So this is like a little shift in what it focussed on this. **BACKLOG** for now. **Then** Ulf talked about Progressive learning (if strategy target is 4, and current level is 0, we need to define LOs for levels 1,2,4). - We need to create a filtering system - that shows these are the LOs for Managers, these are the LOs for common basic understanding Or for level 4 whatever it is. (My reply - So if we have 'SE for managers' selected, then we should show this filtering - that shows - for Managers, this is what they should aim for, and for the rest of the people, we should aim to have at least this level.)

  - Do we show BOTH in pyramid?



B. {Answered} **For the strategy 'Certification'**, we currently do not have target values defined for each competencies in the excel file Qualifizierungsmodule\_Qualifizierungspläne\_v4.xlsx. Marcel has mentioned in his thesis that - "Certification is a part of the 'orientation in the pilot project' strategy". But the 'orientation in the pilot project' strategy has all it's target values as 4 = 'Applying'. I think we have to define the target values for the 'Certification' strategy. **::**  I should define values for this myself. Also similar to Marcel's idea for this.



---



Q2. Role-Based Aggregation vs User Distribution



  Context:

  - We decided that "we can stay on a Role level and not go deep into User level"

  - BUT "Median aggregation" discusses 9/10 users vs 1/10 user scenarios as a drawback



  CRITICAL QUESTION:

  We discussed that the training planning is role-based (not user-based). But the median aggregation discussion we had - talks about user's competency assessment result distributions (9 experts vs 1 beginner).

  "We'll use pure median (per role) for deciding training needs, ignoring user-level distribution (e.g., 9 experts + 1 beginner = median of 'expert' = no training). This would mean that the 1 beginner user belonging to that role would be ignored. Is this correct?"



  A. How do we reconcile these two concepts?



  Scenario:

  - Role: Requirements Engineer (10 users)

  - Competency: Systems Thinking

  - User scores: \[0, 4, 4, 4, 4, 4, 4, 4, 4, 4]

  - Median: 4

  - Role requirement: 4



  What should we show in the pyramid?



  Option A: Pure Role-Based (Median)

  - Median = 4, Requirement = 4 → No gap → Don't show in pyramid

  - The 1 user with score=0 gets ignored



  Option B: Distribution-Aware Role-Based

  - Median = 4, but 10% of users (1/10) have gap

  - Still show in pyramid, but flag as "mostly achieved, minority gap"

  - Or: Show in pyramid ONLY if >X% of role members have gap (what's the threshold?)





  Why This Matters: Determines aggregation algorithm - median alone or distribution-aware.



{Answered} **Ulf's thoughts -** We don't need user level LOs (the users do their individual competency assessment and already get their results with feedbacks and that's it for them.). Instead we need to focus on the whole organisation. We need to understand where does the organisation stand from the competency of the persons who work there. Thus, Ulf thinks it's okay to use the **Median** as the aggregation. **BUT** - we need to consider all possible scenarios to check if the median is the right choice of aggregation. - If we build up a statistics for each of these such scenarios where we visualize a line of values and the middle box being the median, we need to check if there is a big range of values or if it's like every value looks somewhat the same. So - we need a mechanism to visualize this range of values. **Then,** Ulf starts thinking about visualizing the gap - i.e., if one person has a big gap but the others don't have gap, then the median will say that the gap is 0.

Ulf thinks about how will we visualize this information and how we will use it. - **The Goal**: What we want is to have a big list of LOs and we want to eliminate those LOs that were not necessary anymore because people have already reached that level. So, in that case we can use the Median and ignore those people who has not the right level. **But** then again, we think of various situations or scenarios -> if 6 users are at level 2, 6 users are at level 6, and one is at level 4 - then the median will be level 4. Here, many people are untrained and many are very trained. In this situation, we found that Median is not the right choice. The right choice would be to then separate here - the ones who have 6 does not need training and we only focus on the ones who have level 4 or say the ones who have not met the required level. i.e., we can always directly eliminate the users or the roles who have already achieved the target level, and we focus on those who are left. So we will not be considering everyone for the training, but only the ones who have a gap. This information needs to be visualized and made transparent to the admin user who is at the LOs generation page. For instance, an overview saying - this is the target and, so many people (Roles) have achieved it, so many people are below it. So many people much haven't heard about it, so like this kind of Per Competency kind of overview, but then it's like again, a lot of very much information. We need to aggregate this somehow. We could also have the detailed view, but we also need to have an overview for this kind of Roles.

Jomon says: So this was my original question. So Now we are going deep into a single role. We are not just choosing a value for a Role and saying, okay, this is the aggregated median value for that role, but instead we need to actually analyze the user data of those roles and provide this feedback or analysis.

Ulf: I mean, the question would be say in that case, the role requirement level is 4, There's one person Who has not the right level, then Isn't there a need for training? I would say in that case, there is a need for training for one person. So it would mean for me, that there is no need for Customized training. Maybe it's better to bring them on a "Certification" training, so change the selected strategy in that case.

Jomon: So a strategy change that best fits the roles need or that person's need.

Ulf: Correct, so Maybe we need to define this Or you can think about this again between "what is the gap" And "how many people have a gap" And "what is a suitable strategy"? Because I would say in that situation here, the strategy is to give that to provide external training - that he should visit some other training at a company or something. I mean, this is actually something we haven't thought of yet, or it could be also part of "Continuous Support" or something similar Or it could even be "common basic understanding". But that makes it again, more complex. As you see, I still don't have an answer myself yet.

Ulf suggests me to create some scenarios - So you can use Claude AI to create this, say we use 25 persons And we will like for one role and we will go through all these 8 or more different scenarios that will probably occur and based on that, So in that situation I would say, for example, I would recommend - Focus on that competency - So for that Competency Module let's say, I would say, it's not necessary to have a "common basic understanding", maybe The common basic understanding is necessary, but how it is achieved - it's not a training, it will be training on the job, Or Mentoring.

So that "**the method that is used within these strategies"**, and maybe we can have some kind of Separation, based on this here, .... I mean, actually it's like it's not even the strategy. So we will see that, yeah, it could be that we have to change the strategy. It could be just mean that there is more now we have more evidence - "What kind of training should be used in this situation in this specific situation?". So my suggestion would be that you maybe prepare for our next meeting - Some Scenarios, then we will go through these scenarios together, and we'll define what might be the best output here.



---



Q3. Cross-Strategy Validation Logic - not necessary for now.



  Context: "A strategy will apply for all competencies... If the organization's maturity value is low, and everyone can already apply SE in most parts, then "Common basic understanding" strategy might not be the right thing."



  CLARIFICATION NEEDED:

  When validating strategy adequacy, do we:



  Option A: Overall Holistic Check

  - Look at ALL 16 competencies together

  - If MAJORITY (e.g., 70%+) of competencies show current levels >> strategy targets → Strategy too low

  - If MAJORITY of competencies show current levels << strategy targets → Strategy appropriate

  - Decide based on overall picture, not per-competency



  Strategy Validation Threshold



  "When validating strategy adequacy, what percentage of competencies showing 'over-training' (current level > strategy target) should

  trigger a 'Strategy Inadequate' warning?

  - 50% (8 out of 16 competencies)?

  - 70% (11-12 out of 16)?

  - Any other threshold?"



  Also, do we then prompt the user to do a re-evaluation or retake the Maturity Assessment and select the recommended strategies?



{Answered} **Ulf's thoughts -**

It could be also thought that for different competencies, our strategy will differ. But I would say from a system's engineering perspective, it doesn't make sense, because "common basic understanding" means that you like bring everyone together and bridge the gaps; and this could even be sensible if like, let's say 50% of the persons have higher competency in this field, because it's about like Breaking silos; So what I'm saying is that it's not just about the competency level. So the simple answer is, I would say, if 75% (just a random threshold chosen here), We could like have a pop-up **statement** that says we have recognized that you have used, for example, say "Common basic understanding", But the competency assessment has shown that the competency targets achieved this strategy is actually already available and present in the people. And then you can click on change strategy or continue.

And this functionality, we only need this in the low maturity pathway.

Jomon: So for each of the 16 competencies, we do this check if the strategy targets are achieved or not. And we chose a majority percentage check with 75% threshold for example, and then say we need a different strategy since it's already achieved.

Ulf: The only thing is that we maybe have to discuss or think about together about what shall be the statement, because the statement is important that it's like written correctly for me. Because it's not necessary to change the strategy, it's just like we have recognized that people have a lot of competency, and if you really want to focus on breaking the silos, you should anyhow Keep the strategy, But if it comes to the to Bring the people to like Applying (level 4) things, it's not the right strategy you've selected. but actually this question has been asked before. So I'm not to be honest, I'm not even sure if we need this kind of if we really need this kind of double-checking the Strategy selection at the moment, so I would say, let's keep that For now, **Out of scope**. So I know that last time I said we should have it and this time I said we don't need it so maybe next time I will say we need it lol.

And I would say this is not necessary to be implemented for now.



---



Q4. PMT in Low Maturity Organizations



  "Can a low maturity organization select a PMT-requiring strategy like 'Needs-based project-oriented training'? If yes:

  - Should we collect PMT context from them (assuming they might have some processes)?

  - Or always use standard template objectives for low maturity regardless of strategy?"



{Answered} **Ulf's thoughts -**

I would say, if they want to choose it anyway, So our suggestion would be like if they don't have processes or methods or tools defined, and they should go a low maturity path and select the recommended strategies from us. If they have it defined or if they land there but they don't have it defined, then we will ask them, how do you work? And hopefully they will then just by themselves recognize that they have no idea. So, if they continue and they keep everything empty all the time, The system should say that it seems like you don't have those processes, methods and tools defined yet, So we suggest you to change to choose another Strategy. OR, if they typed something in for PMT, it would be fine if they typed something in. Yeah, we'll try to use those inputs as well.

I think this is true as well - if someone is not following our recommendation for the strategies and selecting different strategies in Phase 1, and then it could be also that the system is not working properly because they are not following our recommendation.



---



Q5. Role Assignment to Levels - Granularity - backlog.



  Context: "Based on the gap, you need to know the following 3 competencies... certain roles need to be considered on that level. Then, we could also enter the roles on the side and say - the following roles should visit this training."



  CLARIFICATION NEEDED:

  For the pyramid, when showing "Roles that need this level":



  Scenario:

  - Level 2 of pyramid: "Understanding SE"

  - Competency: Systems Thinking (appears at Level 2)

  - 4 roles in organization: Requirements Engineer, System Architect, Test Engineer, Project Manager

  - Requirements Engineer: 8/10 users need Level 2 for Systems Thinking

  - System Architect: 10/10 users need Level 2 for Systems Thinking

  - Test Engineer: 2/10 users need Level 2 for Systems Thinking

  - Project Manager: 0/10 users need Level 2 for Systems Thinking



  Which roles do we list for "Level 2 - Systems Thinking"?



  Option A: All roles with ANY gap

  - Show: Requirements Engineer, System Architect, Test Engineer

  - (Even if only 2/10 from Test Engineer need it)



  Option B: Roles with MAJORITY gap

  - Show: Requirements Engineer, System Architect

  - (Only if >50% of role members need it)



  Option C: All roles, but with indicators

  - Show:

    - System Architect (critical - all users)

    - Requirements Engineer (majority - 8/10 users)

    - Test Engineer (minority - 2/10 users)





  Why This Matters: Affects how we display role information in the pyramid.



{Answered} **Ulf's thoughts -**

I'm also not a 100% sure yet on how to structure this. I would say in general, my idea at the beginning was that to say alright, This is the competency level - So the pyramid and you can say, this is a Pyramid for the competency of Systems thinking And you see the following Roles need here assistance. Because this is what we say, yeah, on which level do need role assistance, Let's say it like that. So like the gap. So the following role needs here assistance.

And maybe you can then also have it in like in brackets, say, in like 8 of 10 or something and so on. - So that could be one View. The other view is that you say, this is the role, And the role of the requirement's engineering, your competency - Again you have the competencies, and then you say that on level 2, there is assistance necessary in the following competencies to achieve level 4 in the following competencies.

And so I would like to have like these 2 Different views.

The mock html pages you've created goes already in the right direction. On showing Ulf the mock html page, he asks - This is now the competence pyramid for - Is it for a role?, or is it for the competency? (Maybe Ulf's asking about the 2 views).



{Answered} **Another discussion** - We have one specific role cluster in the role competency matrix, which is the "Process and Policy Manager" who has all the high values for all the 16 competencies. We need to consider this specific case. The problem: You are always only responsible for only one process, for example, for the requirements process. So there you need a level 6, but in all the others, you typically don't need the 6. So we need to maybe adapt this. Let's bring this problem to the **Backlog** that we need to that we think about this. I mean, actually, it's quite easy because if they say they are Um, oh no, it's not quite easy. It's only easy for the for the text based input, because if you write - I am responsible for defining requirements, then you can say, alright, You only have the 6 in requirements. But the other way around is that we would need a functionality where we ask if you select role - you are like a process owner or for which process you are responsible and then making the same calculation. So yeah, bring this on the backlog; maybe we'll work on this later on. It's not too important yet here.



---



Q6. Train the Trainer - Internal vs External Decision



  "After selecting 'Train the Trainer' strategy, we ask 'Do you want internal or external trainers?' What should happen based on the answer?

  - Internal trainers → Show full mastery-level learning objectives (they need to become experts)

  - External trainers → Don't show objectives (externally handled)?

  - Or something else?"



---



Q7. Per-Role Pyramid Views - Needed or Not?



  "We discussed that - each role has such pyramids' but 'not sure if we need this.' For the UI, should we:

  - A) One organizational pyramid only, with roles listed WITHIN each level of pyramid

  - B) One organizational pyramid + optional drill-down to see per-role pyramids

  - C) Both views equally important"



---



Q8. Strategy Validation Inputs



  "When validating strategy in a high maturity path, do we compare:

  - A) Current user levels vs Strategy targets only (2-way)

  - B) Current user levels vs Strategy targets vs Role requirements (3-way)



---



Q9. Multiple Strategies in Low Maturity - Target Selection



   Context: Low maturity org selects 2 strategies (e.g., "SE for Managers" + "Common Basic Understanding").



   Scenario:

 	"Common Basic Understanding": Systems Thinking = Level 2

 	"SE for Managers": Systems Thinking = Level 4



Question: Which target do we use?



A) HIGHER target (Level 4) - user confirmed this in feedback

B) Show BOTH strategies separately (user sees Systems Thinking in both strategy tabs)

C) Something else?

