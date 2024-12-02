import httpx
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import traceback
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TinybirdClient')


def log_function_call(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        function_name = func.__name__
        
        # Log the function call
        logger.info(f"Calling {function_name} with args: {args[1:]} kwargs: {kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Successfully completed {function_name} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Exception in {function_name} after {duration:.2f}s: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise
    return wrapper

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

    @log_function_call
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        params['token'] = self.token
        params['__tb__client'] = "tinybird_mcp_claude"
        
        url = f"{self.api_url}/{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    @log_function_call
    async def _post(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        params['token'] = self.token
        params['__tb__client'] = "tinybird_mcp_claude"

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

    async def run_select_query(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Run a SQL SELECT query."""
        kwargs = kwargs or {}
        params = {'q': f'{query} FORMAT JSON', **kwargs}
        return await self._get('v0/sql', params)
    
    async def llms(self, query: str) -> Dict[str, Any]:
        url = "https://www.tinybird.co/docs/llms-full.txt"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def explain(self, pipe_name: str) -> Dict[str, Any]:
        endpoint = f'v0/pipes/{pipe_name}/explain'
        return await self._get(endpoint)
        
    async def save_event(self, datasource_name: str, data: str):
        url = f'{self.api_url}/v0/events'
        params = {
            'name': datasource_name,
            'token': self.token
        }

        try:
            response = await self.client.post(url, params=params, data=data)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise ValueError(str(e))

    async def push_datafile(self, files: str):
        url = f'{self.api_url}/v0/datafiles'

        file_path = Path(files)

        files_dict = {
            file_path.name: (file_path.name, file_path.open('rb'), 'application/octet-stream')
        }

        params = {
            'filenames': file_path.name,
            'force': "True",
            'dry_run': "False",
            'token': self.token
        }

        response = await self.client.post(url, params=params, files=files_dict)
        response.raise_for_status()
        return response.text
