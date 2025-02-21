from typing import Any, Literal, Optional, List, Dict, Union
from pydantic import BaseModel, model_validator


class PM2AppConfig(BaseModel):
    """
    PM2 application configuration model.

    Attributes:
        script (str): The mandatory script path to execute.
        name (Optional[str]): The name of the process.
        args (Optional[List[str]]): Arguments for the script.
        cwd (Optional[str]): The working directory.
        interpreter (Optional[str]): The interpreter to use (e.g., python, node).
        interpreter_args (Optional[List[str]]): Arguments for the interpreter.
        exec_mode (Optional[str]): Execution mode: "fork" or "cluster".
        instances (Optional[Union[int, str]]): Number of instances (integer or "max" for maximum processes).
        autorestart (Optional[bool]): Automatically restart the process on failure.
        watch (Optional[bool]): Enable file watching to restart on changes.
        ignore_watch (Optional[List[str]]): List of directories/files to ignore for watching.
        max_memory_restart (Optional[Union[int, str]]): Memory limit (e.g., 100*1024*1024 or "100M").
        restart_delay (Optional[int]): Delay before restart in milliseconds.
        max_restarts (Optional[int]): Maximum number of restarts allowed.
        env (Optional[Dict[str, Union[str, int, float, bool]]]): Default environment variables.
        env_production (Optional[Dict[str, Union[str, int, float, bool]]]): Environment variables for production.
        error_file (Optional[str]): Path to the error log file.
        out_file (Optional[str]): Path to the output log file.
        pid_file (Optional[str]): File for storing the process PID.
        merge_logs (Optional[bool]): Merge logs from different instances.
        log_date_format (Optional[str]): Date format for logs.
        cron_restart (Optional[str]): CRON expression for scheduled restarts.
        listen_timeout (Optional[int]): Timeout for the listener in milliseconds.
        kill_timeout (Optional[int]): Timeout for graceful process termination in milliseconds.
    """

    script: str
    name: Optional[str] = None  # Process name
    args: Optional[List[str]] = None  # Script arguments
    cwd: Optional[str] = None  # Working directory
    interpreter: Optional[str] = None  # Interpreter (e.g., python, node)
    interpreter_args: Optional[List[str]] = None  # Interpreter arguments

    # Launch settings
    exec_mode: Optional[str] = None  # Execution mode: "fork" or "cluster"
    instances: Optional[Union[int, str]] = (
        None  # Number of instances (integer or "max")
    )
    autorestart: Optional[bool] = True  # Automatically restart on failure
    watch: Optional[bool] = False  # Watch for file changes to restart
    ignore_watch: Optional[List[str]] = None  # Directories/files to ignore for watching

    # Memory and restart limits
    max_memory_restart: Optional[Union[int, str]] = (
        None  # Memory limit (e.g., 100*1024*1024 or "100M")
    )
    restart_delay: Optional[int] = None  # Delay before restart in milliseconds
    max_restarts: Optional[int] = None  # Maximum number of restarts

    # Environment variables
    env: Optional[Dict[str, Union[str, int, float, bool]]] = None  # Default environment
    env_production: Optional[Dict[str, Union[str, int, float, bool]]] = (
        None  # Production environment
    )

    # Logging and PID files
    error_file: Optional[str] = None  # Path to error log file
    out_file: Optional[str] = None  # Path to output log file
    pid_file: Optional[str] = None  # File to store process PID
    merge_logs: Optional[bool] = False  # Merge logs from different instances
    log_date_format: Optional[str] = None  # Date format for logs

    # Additional PM2 parameters
    cron_restart: Optional[str] = None  # CRON expression for app restart
    listen_timeout: Optional[int] = None  # Listener timeout in milliseconds
    kill_timeout: Optional[int] = None  # Timeout for graceful shutdown in milliseconds


class PM2Monit(BaseModel):
    """
    PM2 monitoring data model.

    Attributes:
        memory (Optional[float]): Memory usage.
        cpu (Optional[float]): CPU usage.
    """

    memory: Optional[float] = None
    cpu: Optional[float] = None

    class Config:
        extra = "allow"  # Allow extra fields if they appear


class PM2Env(BaseModel):
    """
    PM2 environment information model.

    Attributes:
        status (Optional[str]): Process status.
        restart_time (Optional[int]): Number of restarts.
        pm_exec_path (Optional[str]): Path to the PM2 executable.
        version (Optional[str]): PM2 version.
        node_version (Optional[str]): Node.js version.
        unstable_restarts (Optional[int]): Count of unstable restarts.
        created_at (Optional[int]): Timestamp when the process was created.
        pm_uptime (Optional[int]): PM2 uptime.
        exec_mode (Optional[str]): Execution mode.
        instances (Optional[int]): Number of instances.
        script_path (Optional[str]): Script path.
        node_args (Optional[List[str]]): Node.js arguments.
        exec_interpreter (Optional[str]): Interpreter used.
        log_file (Optional[str]): Path to the log file.
        out_file (Optional[str]): Path to the output file.
        err_file (Optional[str]): Path to the error file.
        axm_options (Optional[Dict[str, Any]]): Additional options.
    """

    status: Optional[str] = None
    restart_time: Optional[int] = None
    pm_exec_path: Optional[str] = None
    version: Optional[str] = None
    node_version: Optional[str] = None
    unstable_restarts: Optional[int] = None
    created_at: Optional[int] = None
    pm_uptime: Optional[int] = None
    exec_mode: Optional[str] = None
    instances: Optional[int] = None
    script_path: Optional[str] = None
    node_args: Optional[List[str]] = None
    exec_interpreter: Optional[str] = None
    log_file: Optional[str] = None
    out_file: Optional[str] = None
    err_file: Optional[str] = None
    axm_options: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"  # Accept any additional fields


class PM2Process(BaseModel):
    """
    PM2 process model.

    Attributes:
        name (Optional[str]): Process name.
        pm_id (Optional[int]): PM2 assigned process ID.
        pid (Optional[int]): System process ID.
        monit (Optional[PM2Monit]): Monitoring data.
        pm2_env (Optional[PM2Env]): Environment information.
        restart_delay (Optional[int]): Delay before restarting, if applicable.
        namespace (Optional[str]): Process namespace.
    """

    name: Optional[str] = None
    pm_id: Optional[int] = None
    pid: Optional[int] = None
    monit: Optional[PM2Monit] = None
    pm2_env: Optional[PM2Env] = None
    restart_delay: Optional[int] = None  # Additional fields may be present
    namespace: Optional[str] = None

    class Config:
        extra = "allow"  # Store any extra fields provided by PM2


class PM2SuccessResponse(BaseModel):
    """
    Model for a successful PM2 response.

    Attributes:
        status (Literal["success"]): Fixed status value "success".
        data (Union[List[Any], Dict[str, Any]]): Process list or other data structure.
        message (None): No error message on success.
    """

    status: Literal["success"] = "success"
    data: Union[List[Any], Dict[str, Any]]
    message: None = None


class PM2ErrorResponse(BaseModel):
    """
    Model for an error PM2 response.

    Attributes:
        status (Literal["error"]): Fixed status value "error".
        message (str): Error message.
        data (None): No data is returned on error.
    """

    status: Literal["error"] = "error"
    message: str
    data: None = None


class PM2Response(BaseModel):
    """
    Unified PM2 response model that handles both success and error responses.

    Attributes:
        status (Literal["success", "error"]): The response status.
        data (Optional[Union[List[Any], Dict[str, Any]]]): The data returned on success.
        message (Optional[str]): The error message returned on error.

    Validation:
        - If status is "success", then `data` must be provided.
        - If status is "error", then `message` must be provided.
    """

    status: Literal["success", "error"]
    data: Optional[Union[List[Any], Dict[str, Any]]] = None
    message: Optional[str] = None

    @model_validator(mode="before")
    def check_fields(cls, values):
        """
        Validate the input values based on the status field.

        Raises:
            ValueError: If required fields for a given status are missing.
        """
        status = values.get("status")
        if status == "success":
            if "data" not in values or values.get("data") is None:
                raise ValueError("Field 'data' is required for a success response")
        elif status == "error":
            if "message" not in values or values.get("message") is None:
                raise ValueError("Field 'message' is required for an error response")
        else:
            raise ValueError("Invalid status value")
        return values
