# Feature Implementation Plan: "Check and Integrate Existing Offers"

## IMPLEMENTATION STATUS: COMPLETE

**Completed:** 2025-12-11

## Overview

**Feature Name:** Existing Training Offers Integration
**Requested By:** Ulf
**Priority:** High
**Placement:** Learning Objectives Dashboard (Phase2Task3Dashboard.vue), below "Assessment Monitoring" section

### Feature Description
Allow users to select competencies for which their organization already has existing training programs or offers. Selected competencies will be excluded from "Training Requirements Identified" and moved to "No Training Required" with a new tag: **"Training Exists"**.

### User Flow
1. User navigates to Learning Objectives dashboard
2. Below "Assessment Monitoring", a new section displays: **"Existing Training Check"**
3. User sees a prompt: *"Please check if there are certain trainings that already exist in the organization for the listed competencies. These will not be considered for new training development."*
4. User can select/deselect from all 16 competencies via checkboxes
5. Selecting a competency excludes ALL its levels (1, 2, 4) from training requirements
6. When LOs are generated, excluded competencies show in "No Training Required" with "Training Exists" tag
7. This affects Phase 3 module generation (LOs = identified modules)

---

## Technical Analysis

### Current Architecture Summary

**Backend:**
- Core service: `src/backend/app/services/learning_objectives_core.py`
- Key function: `structure_pyramid_output()` - organizes competencies into levels with status flags
- Status values: `training_required`, `achieved`, `not_targeted`
- Cache system with hash invalidation in `GeneratedLearningObjectives` table

**Frontend:**
- Dashboard: `src/frontend/src/components/phase2/task3/Phase2Task3Dashboard.vue`
- Level display: `src/frontend/src/components/phase2/task3/LevelContentView.vue`
- Competency cards: `src/frontend/src/components/phase2/task3/SimpleCompetencyCard.vue`
- Existing tags: "Achieved", "Not Targeted", "Role Met", "Complete"

**Data Flow:**
```
Gap Detection -> structure_pyramid_output() -> Frontend Display
              (apply exclusions here)
```

---

## Implementation Plan

### Phase 1: Database Layer

#### 1.1 New Database Model

**File:** `src/backend/models.py`

```python
class OrganizationExistingTraining(db.Model):
    """
    Stores competencies for which organization has existing training programs.
    These competencies are excluded from LO generation/training requirements.

    Feature: "Check and Integrate Existing Offers" (Ulf's request)
    """
    __tablename__ = 'organization_existing_trainings'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'),
                                 nullable=False, index=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255))  # Username who marked this
    notes = db.Column(db.Text)  # Optional notes about existing training

    # Relationships
    organization = db.relationship('Organization', backref=db.backref(
        'existing_trainings', lazy='dynamic', cascade='all, delete-orphan'
    ))
    competency = db.relationship('Competency')

    # Unique constraint: one entry per org-competency pair
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'competency_id',
                           name='unique_org_competency_training'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'competency_id': self.competency_id,
            'competency_name': self.competency.competency_name if self.competency else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }
```

#### 1.2 Database Migration

**File:** `src/backend/migrations/versions/XXX_add_existing_trainings.py`

```python
"""Add organization_existing_trainings table

Revision ID: XXX
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('organization_existing_trainings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('organization_id', sa.Integer(),
                  sa.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('competency_id', sa.Integer(),
                  sa.ForeignKey('competency.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255)),
        sa.Column('notes', sa.Text()),
        sa.UniqueConstraint('organization_id', 'competency_id',
                           name='unique_org_competency_training')
    )
    op.create_index('idx_existing_trainings_org',
                    'organization_existing_trainings', ['organization_id'])

def downgrade():
    op.drop_table('organization_existing_trainings')
```

---

### Phase 2: Backend API Layer

#### 2.1 New Routes

**File:** `src/backend/app/routes/phase2_learning.py` (extend existing)

```python
# ============================================================
# EXISTING TRAINING OFFERS ENDPOINTS
# ============================================================

@phase2_learning_bp.route('/existing-trainings/<int:organization_id>', methods=['GET'])
def get_existing_trainings(organization_id):
    """
    Get list of competencies marked as having existing training
    """
    try:
        existing = OrganizationExistingTraining.query.filter_by(
            organization_id=organization_id
        ).all()

        # Also get all competencies for selection UI
        all_competencies = Competency.query.order_by(Competency.id).all()

        return jsonify({
            'success': True,
            'data': {
                'existing_training_competencies': [e.competency_id for e in existing],
                'existing_trainings_detail': [e.to_dict() for e in existing],
                'all_competencies': [c.to_dict() for c in all_competencies]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@phase2_learning_bp.route('/existing-trainings/<int:organization_id>', methods=['PUT'])
def update_existing_trainings(organization_id):
    """
    Update the list of competencies with existing training.
    Accepts list of competency_ids to mark as having existing training.
    """
    try:
        data = request.get_json()
        competency_ids = data.get('competency_ids', [])

        # Clear existing entries for this org
        OrganizationExistingTraining.query.filter_by(
            organization_id=organization_id
        ).delete()

        # Add new entries
        for comp_id in competency_ids:
            entry = OrganizationExistingTraining(
                organization_id=organization_id,
                competency_id=comp_id,
                created_by=data.get('username', 'system')
            )
            db.session.add(entry)

        db.session.commit()

        # IMPORTANT: Invalidate LO cache since exclusions changed
        from app.services.learning_objectives_core import invalidate_cache
        invalidate_cache(organization_id)

        return jsonify({
            'success': True,
            'message': f'Updated existing trainings: {len(competency_ids)} competencies marked',
            'competency_ids': competency_ids
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### 2.2 Modify LO Generation Service

**File:** `src/backend/app/services/learning_objectives_core.py`

**Modification 1:** Add helper function to get excluded competencies

```python
def get_excluded_competency_ids(organization_id: int) -> set:
    """
    Get competency IDs that should be excluded from training requirements
    because organization has existing training for them.
    """
    from models import OrganizationExistingTraining

    existing = OrganizationExistingTraining.query.filter_by(
        organization_id=organization_id
    ).all()

    return {e.competency_id for e in existing}
```

**Modification 2:** Update `structure_pyramid_output()` function

In the loop where competencies are processed, add exclusion logic:

```python
def structure_pyramid_output(gaps, main_targets, organization_id, ...):
    """
    ... existing docstring ...
    """

    # NEW: Get excluded competencies (existing training)
    excluded_comp_ids = get_excluded_competency_ids(organization_id)

    # ... existing code ...

    for level in [1, 2, 4, 6]:
        for competency_id in range(1, 19):  # 16-18 competencies
            # ... existing logic to determine status ...

            # NEW: Override status if competency has existing training
            if competency_id in excluded_comp_ids:
                # Force to "no training required" with special status
                status = 'training_exists'  # NEW STATUS VALUE
                grayed_out = True
                # Keep the learning objective text but mark as excluded

            # ... rest of existing code ...

            competency_data = {
                'competency_id': competency_id,
                'competency_name': competency_name,
                'status': status,
                'grayed_out': grayed_out,
                'learning_objective': learning_objective,
                'has_existing_training': competency_id in excluded_comp_ids,  # NEW FIELD
                # ... other fields ...
            }
```

**Modification 3:** Update `compute_input_hash()` to include excluded competencies

```python
def compute_input_hash(organization_id, strategies, pmt_context, ...):
    """
    ... existing docstring ...
    """
    # ... existing code ...

    # NEW: Include excluded competencies in hash
    excluded_ids = sorted(get_excluded_competency_ids(organization_id))

    hash_input = {
        # ... existing fields ...
        'excluded_competencies': excluded_ids,  # NEW
    }

    return hashlib.sha256(json.dumps(hash_input, sort_keys=True).encode()).hexdigest()
```

---

### Phase 3: Frontend Components

#### 3.1 New Component: ExistingTrainingsSelector.vue

**File:** `src/frontend/src/components/phase2/task3/ExistingTrainingsSelector.vue`

```vue
<template>
  <el-card class="existing-trainings-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon :size="20" color="#409EFF"><Box /></el-icon>
          <span class="header-title">Existing Training Check</span>
        </div>
        <el-tag v-if="selectedCount > 0" type="info" size="small">
          {{ selectedCount }} excluded
        </el-tag>
      </div>
    </template>

    <!-- Info Banner -->
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="info-alert"
    >
      <template #title>
        Check for existing training programs
      </template>
      <p>
        Please check if there are certain trainings that already exist in your
        organization for the listed competencies. These will not be considered
        for new training development.
      </p>
    </el-alert>

    <!-- Competency Selection Grid -->
    <div class="competency-grid">
      <div
        v-for="comp in competencies"
        :key="comp.id"
        class="competency-item"
        :class="{ 'is-selected': isSelected(comp.id) }"
        @click="toggleCompetency(comp.id)"
      >
        <el-checkbox
          :model-value="isSelected(comp.id)"
          @change="toggleCompetency(comp.id)"
          @click.stop
        />
        <div class="competency-info">
          <span class="competency-name">{{ comp.name }}</span>
          <span class="competency-area">{{ comp.area }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions-row">
      <el-button size="small" text @click="clearAll" :disabled="selectedCount === 0">
        Clear All
      </el-button>
      <el-button
        type="primary"
        size="small"
        @click="saveSelections"
        :loading="isSaving"
        :disabled="!hasChanges"
      >
        <el-icon><Check /></el-icon>
        Save Selections
      </el-button>
    </div>

    <!-- Note about impact -->
    <p class="impact-note" v-if="selectedCount > 0">
      <el-icon><InfoFilled /></el-icon>
      {{ selectedCount }} competencies will be excluded from training requirements
      (including all levels: Knowing, Understanding, Applying).
    </p>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Check, InfoFilled } from '@element-plus/icons-vue'
import axios from '@/api/axios'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

// State
const competencies = ref([])
const selectedIds = ref(new Set())
const originalIds = ref(new Set())
const isLoading = ref(false)
const isSaving = ref(false)

// Computed
const selectedCount = computed(() => selectedIds.value.size)

const hasChanges = computed(() => {
  if (selectedIds.value.size !== originalIds.value.size) return true
  for (const id of selectedIds.value) {
    if (!originalIds.value.has(id)) return true
  }
  return false
})

// Methods
const isSelected = (id) => selectedIds.value.has(id)

const toggleCompetency = (id) => {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  selectedIds.value = newSet
}

const clearAll = () => {
  selectedIds.value = new Set()
}

const fetchData = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(
      `/api/phase2/existing-trainings/${props.organizationId}`
    )

    if (response.data.success) {
      competencies.value = response.data.data.all_competencies
      const existingIds = response.data.data.existing_training_competencies || []
      selectedIds.value = new Set(existingIds)
      originalIds.value = new Set(existingIds)
    }
  } catch (error) {
    console.error('[ExistingTrainings] Fetch error:', error)
    ElMessage.error('Failed to load existing trainings data')
  } finally {
    isLoading.value = false
  }
}

const saveSelections = async () => {
  try {
    isSaving.value = true

    const response = await axios.put(
      `/api/phase2/existing-trainings/${props.organizationId}`,
      {
        competency_ids: Array.from(selectedIds.value)
      }
    )

    if (response.data.success) {
      originalIds.value = new Set(selectedIds.value)
      ElMessage.success('Existing training selections saved')
      emit('updated')
    }
  } catch (error) {
    console.error('[ExistingTrainings] Save error:', error)
    ElMessage.error('Failed to save selections')
  } finally {
    isSaving.value = false
  }
}

// Lifecycle
onMounted(fetchData)
</script>

<style scoped>
.existing-trainings-card {
  border-left: 4px solid #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-weight: 600;
  font-size: 16px;
}

.info-alert {
  margin-bottom: 20px;
}

.info-alert p {
  margin: 8px 0 0 0;
  font-size: 14px;
  line-height: 1.5;
}

.competency-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.competency-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.competency-item:hover {
  background: #ecf5ff;
  border-color: #409EFF;
}

.competency-item.is-selected {
  background: #e6f7ff;
  border-color: #409EFF;
}

.competency-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.competency-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.competency-area {
  font-size: 12px;
  color: #909399;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.impact-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 16px 0 0 0;
  padding: 12px;
  background: #fdf6ec;
  border-radius: 6px;
  font-size: 13px;
  color: #e6a23c;
}
</style>
```

#### 3.2 Update Dashboard Layout

**File:** `src/frontend/src/components/phase2/task3/Phase2Task3Dashboard.vue`

Add new section between "Assessment Monitoring" and "Organization SE Practices":

```vue
<!-- SECTION 1.5: Existing Training Check (NEW) -->
<div class="section-container">
  <h2 class="section-heading">
    <el-icon><Box /></el-icon>
    Existing Training Check
  </h2>
  <ExistingTrainingsSelector
    :organization-id="organizationId"
    @updated="handleExistingTrainingsUpdated"
  />
</div>
```

Add import and handler:

```javascript
import ExistingTrainingsSelector from './ExistingTrainingsSelector.vue'

const handleExistingTrainingsUpdated = () => {
  // Refresh prerequisites/data since exclusions changed
  refreshData()
  ElMessage.info('Note: You may need to regenerate learning objectives to apply changes.')
}
```

#### 3.3 Update SimpleCompetencyCard.vue

Add new status handling for "Training Exists":

```javascript
// In achievedLabel computed property, add:
const achievedLabel = computed(() => {
  const status = props.competency.status

  // NEW: Check for existing training status
  if (status === 'training_exists' || props.competency.has_existing_training) {
    return 'Training Exists'
  }

  if (status === 'target_achieved' || status === 'achieved') {
    return 'Achieved'
  }
  // ... rest of existing code
})
```

Add new badge styling:

```vue
<!-- Update achieved-badge div -->
<div v-else-if="!isTTT && !hasSkillGap" class="achieved-badge"
     :class="{
       'not-targeted': isNotTargeted,
       'training-exists': hasExistingTraining  // NEW
     }">
```

```css
/* NEW: Training Exists badge styling */
.achieved-badge.training-exists {
  background: #e6f4ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}
```

Add computed property:

```javascript
const hasExistingTraining = computed(() => {
  return props.competency.status === 'training_exists' ||
         props.competency.has_existing_training === true
})
```

#### 3.4 Update LevelContentView.vue

Add new stat for "Training Exists" count:

```vue
<!-- In header-stats div, add: -->
<div class="stat-item training-exists" v-if="trainingExistsCount > 0">
  <span class="stat-value">{{ trainingExistsCount }}</span>
  <span class="stat-label">Training Exists</span>
</div>
```

```javascript
// Add computed property
const trainingExistsCount = computed(() => {
  return props.competencies.filter(c =>
    c.status === 'training_exists' || c.has_existing_training
  ).length
})
```

```css
/* NEW styling */
.stat-item.training-exists {
  background: rgba(24, 144, 255, 0.2);
}
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `src/backend/models.py` | MODIFY | Add `OrganizationExistingTraining` model |
| `src/backend/migrations/versions/XXX_*.py` | CREATE | Migration for new table |
| `src/backend/app/routes/phase2_learning.py` | MODIFY | Add GET/PUT endpoints |
| `src/backend/app/services/learning_objectives_core.py` | MODIFY | Add exclusion logic in `structure_pyramid_output()`, update hash |
| `src/frontend/src/components/phase2/task3/ExistingTrainingsSelector.vue` | CREATE | New component for selection UI |
| `src/frontend/src/components/phase2/task3/Phase2Task3Dashboard.vue` | MODIFY | Add new section |
| `src/frontend/src/components/phase2/task3/SimpleCompetencyCard.vue` | MODIFY | Add "Training Exists" tag |
| `src/frontend/src/components/phase2/task3/LevelContentView.vue` | MODIFY | Add "Training Exists" stat |

---

## Testing Checklist

### Backend Tests
- [ ] GET /existing-trainings returns all competencies and current selections
- [ ] PUT /existing-trainings saves selections correctly
- [ ] Cache is invalidated when selections change
- [ ] LO generation excludes selected competencies from training_required
- [ ] Excluded competencies appear with status='training_exists'
- [ ] Hash changes when exclusions change (forcing regeneration)

### Frontend Tests
- [ ] Existing training selector displays all 16 competencies
- [ ] Checkboxes toggle correctly
- [ ] Save button only enabled when changes exist
- [ ] Success message appears on save
- [ ] Dashboard refreshes after save
- [ ] "Training Exists" tag appears in competency cards
- [ ] Stats update to show "Training Exists" count

### Integration Tests
- [ ] Select 3 competencies -> Generate LOs -> Verify 3 appear in "No Training Required" with "Training Exists"
- [ ] Unselect 1 -> Regenerate -> Verify 1 moves back to "Training Required"
- [ ] Verify all levels (1, 2, 4) of excluded competency show as excluded

---

## Implementation Order

1. **Database Layer** (30 min)
   - Add model to `models.py`
   - Create and run migration

2. **Backend API** (1 hour)
   - Add GET/PUT routes
   - Implement `get_excluded_competency_ids()`
   - Modify `structure_pyramid_output()`
   - Update `compute_input_hash()`

3. **Frontend Components** (2 hours)
   - Create `ExistingTrainingsSelector.vue`
   - Update `Phase2Task3Dashboard.vue`
   - Update `SimpleCompetencyCard.vue`
   - Update `LevelContentView.vue`

4. **Testing & Polish** (1 hour)
   - Test full flow
   - Fix edge cases
   - Verify Phase 3 impact

**Total Estimated Effort:** 4-5 hours

---

## Future Considerations

1. **Bulk Operations**: Add "Select All" / "Deselect All" buttons
2. **Notes Field**: Allow users to add notes about existing training provider
3. **Reporting**: Include excluded competencies in Excel export with "Training Exists" flag
4. **Audit Trail**: Log who made changes and when
5. **Phase 3 Integration**: Ensure module generation respects exclusions

---

## Questions for Clarification (Optional)

1. Should there be an undo/history feature for exclusion changes?
2. Should excluded competencies be shown differently in exports?
3. Should we notify users if they try to generate LOs without checking this section?
