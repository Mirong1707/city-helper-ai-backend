# Agent Architecture - City Helper

## Pipeline Flow

```
┌─────────────┐
│   User      │ "Top 5 bars in Munich"
│  (Frontend) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  STEP 1: Intent Detection & Query Classification   │ │
│  │  ────────────────────────────────────────────────  │ │
│  │  Input: User message string                        │ │
│  │  Output: Query type + structured parameters        │ │
│  │                                                     │ │
│  │  OpenAI API (GPT-4o-mini with Structured Output)   │ │
│  │  - Extract: location, place_type, count, theme     │ │
│  │  - Validate if it's a route/place request          │ │
│  │  - Return JSON with classification                 │ │
│  └────────────────────────────────────────────────────┘ │
│         │                                                │
│         ▼                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  STEP 2: Intelligent Place Suggestions             │ │
│  │  ────────────────────────────────────────────────  │ │
│  │  OpenAI generates list of SPECIFIC place names     │ │
│  │                                                     │ │
│  │  Prompt: "Give me 5 best bars in Munich"           │ │
│  │  Response (structured):                             │ │
│  │  [                                                  │ │
│  │    "Hofbräuhaus München",                          │ │
│  │    "Augustiner-Bräu",                              │ │
│  │    "Viktualienmarkt Beer Garden",                  │ │
│  │    ...                                              │ │
│  │  ]                                                  │ │
│  └────────────────────────────────────────────────────┘ │
│         │                                                │
│         ▼                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  STEP 3: Get Real Location Data                    │ │
│  │  ────────────────────────────────────────────────  │ │
│  │  Google Places API - Text Search                   │ │
│  │                                                     │ │
│  │  For each place name:                               │ │
│  │    - Search: "Hofbräuhaus München, Munich"         │ │
│  │    - Get: coordinates, address, place_id, rating   │ │
│  │    - Get: opening hours, photos (optional)          │ │
│  └────────────────────────────────────────────────────┘ │
│         │                                                │
│         ▼                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  STEP 4: Generate Maps URLs                        │ │
│  │  ────────────────────────────────────────────────  │ │
│  │  Build Google Maps links:                           │ │
│  │                                                     │ │
│  │  - Individual place links (for each point)          │ │
│  │  - Embed map URL for full route view                │ │
│  │  - Directions links between points (segments)       │ │
│  │  - Walking/driving route optimization               │ │
│  └────────────────────────────────────────────────────┘ │
│         │                                                │
│         ▼                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  STEP 5: Format Response for Frontend              │ │
│  │  ────────────────────────────────────────────────  │ │
│  │  {                                                  │ │
│  │    "response": "AI message text",                   │ │
│  │    "workspace": {                                   │ │
│  │      "type": "map",                                 │ │
│  │      "data": {                                      │ │
│  │        "title": "Top 5 Bars in Munich",             │ │
│  │        "points": [...],  // MapPoint[]              │ │
│  │        "segments": [...], // MapSegment[]           │ │
│  │        "fullRouteMapUrl": "...",                    │ │
│  │        "fullRouteLink": "..."                       │ │
│  │      }                                               │ │
│  │    }                                                 │ │
│  │  }                                                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │   Frontend     │ Displays map with MapView
          │   (React)      │ component
          └────────────────┘
```

## Data Models

### Step 1 Output: Query Classification
```python
class QueryClassification(BaseModel):
    is_route_request: bool
    location: str  # "Munich", "Saint Petersburg"
    place_type: str  # "bars", "museums", "parks"
    count: int  # 3, 5, 10
    theme: Optional[str]  # "modern art", "craft beer"
    travel_mode: str  # "walking", "driving", "transit"
```

### Step 2 Output: Place Suggestions
```python
class PlaceSuggestion(BaseModel):
    name: str
    short_description: str
    why_recommended: str

class PlaceSuggestions(BaseModel):
    places: List[PlaceSuggestion]
    route_description: str
```

### Step 3 Output: Enriched Places
```python
class EnrichedPlace(BaseModel):
    name: str
    description: str
    address: str
    coordinates: dict  # {"lat": 48.xx, "lng": 11.xx}
    place_id: str
    rating: Optional[float]
    google_maps_link: str
```

### Step 5 Output: Final Response (matches MapView props)
```typescript
{
  response: string,
  workspace: {
    type: "map",
    data: {
      title: string,
      description: string,
      duration: string,
      points: MapPoint[],  // {name, googleMapsLink}
      segments: MapSegment[],  // {from, to, mapUrl}
      fullRouteMapUrl: string,  // embed URL
      fullRouteLink: string  // Google Maps directions
    }
  }
}
```

## Error Handling

### Case 1: Not a route request
```json
{
  "response": "Sorry, I can help with route planning. Try asking...",
  "workspace": {"type": "empty"}
}
```

### Case 2: Location not found
```json
{
  "response": "I couldn't find places matching your request...",
  "workspace": {"type": "empty"}
}
```

### Case 3: API failures
- Retry logic for transient errors
- Fallback to mock data for demos
- Clear error messages to user

## Environment Variables Needed

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Google Cloud
GOOGLE_PLACES_API_KEY=AIza...
GOOGLE_MAPS_API_KEY=AIza...  # Can be same as Places key

# Optional: Feature flags
ENABLE_REAL_API=true  # false = use mocks for development
```

## Cost Estimation (per request)

**Full pipeline execution:**
- OpenAI calls (2x): ~$0.0003 (GPT-4o-mini)
- Google Places API (5 places): ~$0.017
- **Total: ~$0.02 per route request**

For 100 test requests: **~$2**
For 1000 users/month (10 routes each): **~$200**

## Implementation Order

1. ✅ Setup: Add API keys to env
2. ✅ Step 1: Query classification with OpenAI
3. ✅ Step 2: Place suggestions with OpenAI
4. ✅ Step 3: Google Places integration
5. ✅ Step 4: Maps URL generation
6. ✅ Step 5: Response formatting
7. ✅ Integration test: Full pipeline
8. ✅ Frontend update: Connect to real backend

## Files to Create/Modify

```
city-helper-ai-backend/
├── app/
│   ├── services/
│   │   ├── chat_service.py         [MODIFY] - orchestrate pipeline
│   │   ├── openai_service.py       [NEW] - OpenAI API calls
│   │   ├── places_service.py       [NEW] - Google Places API
│   │   └── maps_service.py         [NEW] - URL generation
│   ├── schemas/
│   │   └── agent.py                [NEW] - data models
│   └── core/
│       └── config/
│           └── secrets.py          [MODIFY] - add API keys
```

## Next Steps

1. Get API keys
2. Add to .env file
3. Implement services one by one
4. Test each step independently
5. Integrate full pipeline
