import {Dropzone, MIME_TYPES} from '@mantine/dropzone';

export default function ImageMatchContainer () {

    return (
        <Dropzone
            accept={[
                MIME_TYPES.png,
                MIME_TYPES.jpeg
            ]}
            onDrop={() => { console.log('Dropzone dropped'); }}
            onReject={() => { console.log('Dropzone rejected'); }}
        >
            {/* children */}
            <b>Hello World</b>
        </Dropzone>
    );
}