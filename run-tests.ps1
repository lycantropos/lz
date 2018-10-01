docker-compose up --build --exit-code-from lz

$STATUS = $LastExitCode

docker-compose down --remove-orphans

if ($STATUS -eq 0)
{
    echo "Tests passed"
}
else
{
    echo "Tests failed to pass"
}

exit $STATUS
