import httpx
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Column:
    name: str
    type: str
    codec: Optional[str]
    default_value: Optional[str]
    jsonpath: Optional[str]
    nullable: bool
    normalized_name: str

@dataclass
class Engine:
    engine: str
    engine_sorting_key: str
    engine_partition_key: str
    engine_primary_key: Optional[str]

@dataclass
class DataSource:
    id: str
    name: str
    engine: Engine
    columns: List[Column]
    indexes: List[Any]
    new_columns_detected: Dict[str, Any]
    quarantine_rows: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSource':
        engine = Engine(**data['engine'])
        columns = [Column(**col) for col in data['columns']]
        return cls(
            id=data['id'],
            name=data['name'],
            engine=engine,
            columns=columns,
            indexes=data['indexes'],
            new_columns_detected=data['new_columns_detected'],
            quarantine_rows=data['quarantine_rows']
        )

@dataclass
class Pipe:
    type: str
    id: str
    name: str
    description: Optional[str]
    endpoint: Optional[str]
    url: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipe':
        return cls(**data)

@dataclass
class PipeData:
    meta: List[Dict[str, str]]
    data: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipeData':
        return cls(**data)

class APIClient:
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "User-Agent": "Python/APIClient"
            }
        )
        self.insights: list[str] = []

    def _synthesize_memo(self) -> str:
        if not self.insights:
            return "No insights have been discovered yet."

        insights = "\n".join(f"- {insight}" for insight in self.insights)

        memo = "📊 Analysis Memo 📊\n\n"
        memo += "Key Insights Discovered:\n\n"
        memo += insights

        if len(self.insights) > 1:
            memo += "\nSummary:\n"
            memo += f"Analysis has revealed {len(self.insights)} key insights."

        return memo

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        params['token'] = self.token
        
        url = f"{self.api_url}/{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def list_data_sources(self) -> List[DataSource]:
        """List all available data sources."""
        params = {'attrs': 'id,name,description,columns'}
        response = await self._get('v0/datasources', params)
        return [DataSource.from_dict(ds) for ds in response['datasources']]

    async def get_data_source(self, datasource_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific data source."""
        params = {
            'attrs': 'columns',
        }
        return await self._get(f'v0/datasources/{datasource_id}', params)

    async def list_pipes(self) -> List[Pipe]:
        """List all available pipes."""
        params = {'attrs': 'id,name,description,type,endpoint'}
        response = await self._get('v0/pipes', params)
        return [Pipe.from_dict(pipe) for pipe in response['pipes']]

    async def get_pipe(self, pipe_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific pipe."""
        return await self._get(f'v0/pipes/{pipe_name}')

    async def get_pipe_data(self, pipe_name: str, **params) -> PipeData:
        """Get data from a pipe with optional parameters."""
        response = await self._get(f'v0/pipes/{pipe_name}.json', params)
        return PipeData.from_dict({key: response[key] for key in ['meta', 'data'] if key in response})

    async def run_select_query(self, query: str) -> Dict[str, Any]:
        """Run a SQL SELECT query."""
        params = {'q': f'{query} FORMAT JSON'}
        return await self._get('v0/sql', params)
    
    async def llms(self, query: str) -> Dict[str, Any]:
        url = "https://www.tinybird.co/docs/llms.txt"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        
    async def save_event(self, datasource_name: str, data: Dict[str, Any]):
        url = f'{self.client.api_url}/v0/events'
        params = {
            'name': datasource_name,
            'token': self.client.token
        }

        response = await self.client.post(url, params=params, data=data)
        response.raise_for_status()
        return response.text

