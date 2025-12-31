import {Box, TextInput} from "@mantine/core";
import {useForm} from "@mantine/form";

export default function TextSearchForm() {
    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            searchText: ''
        },

        validate: {
            searchText: (value: string) => value.length > 0 ? null : 'You must enter a search term'
        }
    });

    return (
        <form className="text-search" onSubmit={form.onSubmit((values) => console.log(values))}>
            <Box
                mx="auto"
                w={400}
            >
                <TextInput
                    placeholder="Image Description"
                    key={form.key('searchText')}
                    {...form.getInputProps('searchText')}
                />
            </Box>
        </form>
    )
}